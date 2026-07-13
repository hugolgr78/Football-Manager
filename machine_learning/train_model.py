"""
train_model.py

First-iteration model: predicts the actual match score - two numbers, a
home goals count and an away goals count - from the 620-column dataset
built by dataset_builder.py (per-player mental, physical, technical, and gk
attributes for both lineups, plus formations).

Goals are counts, not continuous values, so this uses Poisson regression
(the standard approach in football analytics - e.g. Dixon-Coles-style
models) rather than plain regression: the network outputs a log-rate for
each side, and is trained with Poisson negative log-likelihood
(nn.PoissonNLLLoss) instead of MSE. At inference, exponentiating the output
gives the predicted expected goals for each side.

Pipeline:
  1. Load final_dataset.csv (or several, if you have more than one output
     file from splitting the games across runs - just list them all).
  2. Targets are home_score and away_score directly (no longer collapsed
     into win/draw/loss) - both columns are then dropped from the features.
  3. One-hot encode home_formation / away_formation.
  4. Every other column is a numeric sofifa attribute - coerced to numeric,
     with missing/blank values median-imputed (stats computed on the
     training split only, to avoid leaking validation data into training).
  5. Standardize the numeric features (again, fit on train only).
  6. Train a small feedforward network with two output heads (home log-rate,
     away log-rate), tracking train/val Poisson loss per epoch, with early
     stopping on the best validation loss.
  7. Print a clear final summary: final train/val loss, MAE on each side's
     predicted goals, and two bonus interpretability metrics - exact
     scoreline accuracy, and match-outcome accuracy (comparing predicted
     rates to derive win/draw/loss, same framing as a classifier would).
  8. Save the trained model + all preprocessing artifacts (scaler, imputer
     medians, formation categories, feature column order) to disk, so you
     can reload everything identically for iteration 2 or for prediction
     (see predict_example.py) without refitting preprocessing from scratch.

Usage:
    python train_model.py --data machine_learning/final_dataset.csv
    python train_model.py --data final_dataset_part1.csv final_dataset_part2.csv
"""

import argparse
import pickle

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SCORE_COLUMNS = ["home_score", "away_score"]
FORMATION_COLUMNS = ["home_formation", "away_formation"]

HIDDEN_SIZES = [256, 128, 64]
DROPOUT = 0.3
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
BATCH_SIZE = 256
EPOCHS = 60
EARLY_STOPPING_PATIENCE = 10  # stop if val_loss hasn't improved in this many epochs
VAL_FRACTION = 0.15
RANDOM_SEED = 42

MODEL_OUTPUT_PATH = "machine_learning/match_score_model_v1.pt"
PREPROCESSING_OUTPUT_PATH = "machine_learning/match_score_preprocessing_v1.pkl"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---------------------------------------------------------------------------
# Data loading & preprocessing
# ---------------------------------------------------------------------------
def load_dataset(paths):
    frames = [pd.read_csv(p, low_memory=False) for p in paths]
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    print(f"Loaded {len(df)} rows from {len(paths)} file(s), {len(df.columns)} columns.")
    return df


def derive_targets(df):
    """Returns (df, y) where y is an (N, 2) float array of [home_goals, away_goals].
    Rows with unparseable scores are dropped."""
    home_goals = pd.to_numeric(df["home_score"], errors="coerce")
    away_goals = pd.to_numeric(df["away_score"], errors="coerce")

    valid = home_goals.notna() & away_goals.notna()
    if not valid.all():
        dropped = (~valid).sum()
        print(f"Dropping {dropped} row(s) with unparseable home_score/away_score.")
        df = df[valid].reset_index(drop=True)
        home_goals = home_goals[valid].reset_index(drop=True)
        away_goals = away_goals[valid].reset_index(drop=True)

    y = np.stack([home_goals.to_numpy(), away_goals.to_numpy()], axis=1).astype(np.float32)
    return df, y


def build_features(df, formation_categories=None, feature_columns=None, imputer_medians=None, scaler=None, fit=True):
    """
    Builds the numeric feature matrix from a dataframe.

    fit=True (training set): learns formation categories, imputation medians,
      and the scaler from this data, and returns them alongside the matrix.
    fit=False (val set / future inference): reuses the already-fitted
      artifacts passed in, so nothing leaks from val into the fitted stats.
    """
    df = df.drop(columns=SCORE_COLUMNS, errors="ignore")

    # --- One-hot encode formations ---
    formation_df = df[FORMATION_COLUMNS].astype(str)
    if fit:
        formation_categories = {col: sorted(formation_df[col].unique()) for col in FORMATION_COLUMNS}

    formation_encoded_parts = []
    for col in FORMATION_COLUMNS:
        cats = formation_categories[col]
        for cat in cats:
            formation_encoded_parts.append((formation_df[col] == cat).astype(np.float32).rename(f"{col}={cat}"))
    formation_encoded = pd.concat(formation_encoded_parts, axis=1) if formation_encoded_parts else pd.DataFrame(index=df.index)

    # --- Numeric attribute columns (everything else) ---
    numeric_df = df.drop(columns=FORMATION_COLUMNS, errors="ignore")
    numeric_df = numeric_df.apply(pd.to_numeric, errors="coerce")

    if fit:
        feature_columns = list(numeric_df.columns)
        imputer_medians = numeric_df.median(numeric_only=True)

    numeric_df = numeric_df[feature_columns]
    numeric_df = numeric_df.fillna(imputer_medians)
    # Any column that's entirely NaN in this split (median itself is NaN) -> 0
    numeric_df = numeric_df.fillna(0.0)

    if fit:
        scaler = StandardScaler()
        numeric_scaled = scaler.fit_transform(numeric_df.values.astype(np.float32))
    else:
        numeric_scaled = scaler.transform(numeric_df.values.astype(np.float32))

    X = np.concatenate([numeric_scaled, formation_encoded.values.astype(np.float32)], axis=1)

    artifacts = {
        "formation_categories": formation_categories,
        "feature_columns": feature_columns,
        "imputer_medians": imputer_medians,
        "scaler": scaler,
    }
    return X.astype(np.float32), artifacts


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class MatchScoreNet(nn.Module):
    """Outputs two raw log-rates: [log(home_goal_rate), log(away_goal_rate)].
    No final activation - PoissonNLLLoss(log_input=True) expects raw log-rates
    directly and applies the exp() internally (more numerically stable than
    exponentiating ourselves before the loss)."""

    def __init__(self, input_dim, hidden_sizes=HIDDEN_SIZES, dropout=DROPOUT):
        super().__init__()
        layers = []
        prev_size = input_dim
        for hidden_size in hidden_sizes:
            layers += [nn.Linear(prev_size, hidden_size), nn.ReLU(), nn.Dropout(dropout)]
            prev_size = hidden_size
        layers.append(nn.Linear(prev_size, 2))  # [home_log_rate, away_log_rate]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train(X_train, y_train, X_val, y_val, input_dim,
          hidden_sizes=HIDDEN_SIZES, dropout=DROPOUT,
          learning_rate=LEARNING_RATE, weight_decay=WEIGHT_DECAY,
          batch_size=BATCH_SIZE, epochs=EPOCHS, patience=EARLY_STOPPING_PATIENCE,
          verbose=True):
    torch.manual_seed(RANDOM_SEED)

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_val_t = torch.tensor(X_val, dtype=torch.float32).to(DEVICE)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).to(DEVICE)

    train_dataset = torch.utils.data.TensorDataset(X_train_t, y_train_t)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    model = MatchScoreNet(input_dim, hidden_sizes=hidden_sizes, dropout=dropout).to(DEVICE)
    # full=True includes the Stirling-approximation term, so the reported
    # loss is a proper Poisson NLL value rather than missing a constant term.
    criterion = nn.PoissonNLLLoss(log_input=True, full=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=max(1, patience // 2))

    best_val_loss = float("inf")
    best_state_dict = None
    best_epoch = 0
    epochs_without_improvement = 0

    final_train_loss = None
    final_val_loss = None

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss_sum = 0.0
        epoch_examples = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            epoch_loss_sum += loss.item() * xb.size(0)
            epoch_examples += xb.size(0)
        train_loss = epoch_loss_sum / epoch_examples

        model.eval()
        with torch.no_grad():
            val_preds = model(X_val_t)
            val_loss = criterion(val_preds, y_val_t).item()
        scheduler.step(val_loss)

        final_train_loss = train_loss
        final_val_loss = val_loss

        if verbose and (epoch == 1 or epoch % 5 == 0 or epoch == epochs):
            current_lr = optimizer.param_groups[0]["lr"]
            print(f"Epoch {epoch:3d}/{epochs} - train_loss: {train_loss:.4f} - val_loss: {val_loss:.4f} - lr: {current_lr:.2e}")

        # Track the best checkpoint by val_loss - the last epoch isn't
        # necessarily the best one, so we restore the best-performing
        # weights before reporting final numbers.
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state_dict = {k: v.clone() for k, v in model.state_dict().items()}
            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                if verbose:
                    print(f"Early stopping at epoch {epoch} (no val_loss improvement in {patience} epochs).")
                break

    model.load_state_dict(best_state_dict)
    if verbose:
        print(f"Restored best checkpoint from epoch {best_epoch} (val_loss={best_val_loss:.4f}).")

    model.eval()
    with torch.no_grad():
        val_preds_log = model(X_val_t)
        final_val_loss = criterion(val_preds_log, y_val_t).item()

        train_preds_log = model(X_train_t.to(DEVICE))
        final_train_loss = criterion(train_preds_log, y_train_t.to(DEVICE)).item()

    return model, final_train_loss, final_val_loss


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------
def predicted_rates(model, X):
    """Runs the model and exponentiates its output to get expected goals
    (the Poisson rate) for each side. Shape (N, 2): [home_rate, away_rate]."""
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X, dtype=torch.float32).to(DEVICE)
        log_rates = model(X_t)
        rates = torch.exp(log_rates).cpu().numpy()
    return rates


def derive_outcome(home, away):
    """0 = home win, 1 = draw, 2 = away win - works on either actual goal
    counts or predicted rates (comparing rates directly, without rounding
    first, is the more principled way to derive a predicted outcome)."""
    return np.where(home > away, 0, np.where(home == away, 1, 2))


def evaluate(model, X_val, y_val):
    rates = predicted_rates(model, X_val)
    home_pred_rate, away_pred_rate = rates[:, 0], rates[:, 1]
    home_actual, away_actual = y_val[:, 0], y_val[:, 1]

    home_mae = mean_absolute_error(home_actual, home_pred_rate)
    away_mae = mean_absolute_error(away_actual, away_pred_rate)

    home_pred_rounded = np.round(home_pred_rate)
    away_pred_rounded = np.round(away_pred_rate)
    exact_scoreline_acc = np.mean((home_pred_rounded == home_actual) & (away_pred_rounded == away_actual))

    predicted_outcome = derive_outcome(home_pred_rate, away_pred_rate)
    actual_outcome = derive_outcome(home_actual, away_actual)
    outcome_acc = np.mean(predicted_outcome == actual_outcome)

    return {
        "home_mae": home_mae,
        "away_mae": away_mae,
        "exact_scoreline_accuracy": exact_scoreline_acc,
        "outcome_accuracy": outcome_acc,
    }


def main(data_paths, model_out, preprocessing_out):
    df = load_dataset(data_paths)
    df, y = derive_targets(df)

    train_idx, val_idx = train_test_split(df.index, test_size=VAL_FRACTION, random_state=RANDOM_SEED)
    train_df = df.loc[train_idx].reset_index(drop=True)
    val_df = df.loc[val_idx].reset_index(drop=True)
    y_train = y[train_idx.to_numpy()]
    y_val = y[val_idx.to_numpy()]

    X_train, artifacts = build_features(train_df, fit=True)
    X_val, _ = build_features(
        val_df,
        formation_categories=artifacts["formation_categories"],
        feature_columns=artifacts["feature_columns"],
        imputer_medians=artifacts["imputer_medians"],
        scaler=artifacts["scaler"],
        fit=False,
    )

    print(f"Feature matrix: {X_train.shape[1]} features, {X_train.shape[0]} train rows, {X_val.shape[0]} val rows.")
    print(f"Average actual goals - home: {y_train[:, 0].mean():.2f}, away: {y_train[:, 1].mean():.2f}")

    model, final_train_loss, final_val_loss = train(X_train, y_train, X_val, y_val, input_dim=X_train.shape[1])

    metrics = evaluate(model, X_val, y_val)

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Final train loss (Poisson NLL): {final_train_loss:.4f}")
    print(f"Final val loss (Poisson NLL):   {final_val_loss:.4f}")
    print(f"Home goals MAE: {metrics['home_mae']:.3f}")
    print(f"Away goals MAE: {metrics['away_mae']:.3f}")
    print(f"Exact scoreline accuracy: {metrics['exact_scoreline_accuracy']:.4f}")
    print(f"Derived match-outcome accuracy: {metrics['outcome_accuracy']:.4f}")
    print("=" * 60)

    torch.save({
        "model_state_dict": model.state_dict(),
        "input_dim": X_train.shape[1],
        "hidden_sizes": HIDDEN_SIZES,
        "dropout": DROPOUT,
    }, model_out)

    with open(preprocessing_out, "wb") as f:
        pickle.dump(artifacts, f)

    print(f"\nModel saved to {model_out}")
    print(f"Preprocessing artifacts saved to {preprocessing_out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", nargs="+", default=["machine_learning/final_dataset.csv"],
                         help="One or more dataset CSV paths (space-separated) to concatenate")
    parser.add_argument("--model-out", default=MODEL_OUTPUT_PATH)
    parser.add_argument("--preprocessing-out", default=PREPROCESSING_OUTPUT_PATH)
    args = parser.parse_args()

    main(args.data, args.model_out, args.preprocessing_out)