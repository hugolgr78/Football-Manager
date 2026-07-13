"""
tune_model.py

Random hyperparameter search for the match-score model, built directly on
top of train_model.py (reuses its data loading, preprocessing, model class,
and training loop - nothing is duplicated).

Rather than an exhaustive grid (which blows up fast with 5 hyperparameters),
this samples N_TRIALS random combinations from the search space, trains each
with a shorter budget (SEARCH_EPOCHS/SEARCH_PATIENCE) for speed, ranks them
by validation loss, then re-trains the single best combination with the full
training budget (EPOCHS/EARLY_STOPPING_PATIENCE from train_model.py) to
produce the final model.

The train/val split is fixed (same random seed) across every trial, so
trials are directly comparable to each other.

Usage:
    python tune_model.py --data machine_learning/final_dataset.csv --trials 15
"""

import argparse
import pickle
import random

import pandas as pd
import torch

from train_model import (
    load_dataset, derive_targets, build_features, train, evaluate,
    RANDOM_SEED, VAL_FRACTION,
    EPOCHS, EARLY_STOPPING_PATIENCE,
    MODEL_OUTPUT_PATH, PREPROCESSING_OUTPUT_PATH,
)
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Search space - edit these lists to widen/narrow what gets tried
# ---------------------------------------------------------------------------
SEARCH_SPACE = {
    "hidden_sizes": [
        [128, 64],
        [256, 128, 64],
        [256, 128, 64, 32],
        [512, 256, 128],
        [128, 128, 64],
    ],
    "dropout": [0.1, 0.2, 0.3, 0.4, 0.5],
    "learning_rate": [1e-3, 5e-4, 2e-4, 1e-4],
    "weight_decay": [0.0, 1e-5, 1e-4, 1e-3],
    "batch_size": [64, 128, 256, 512],
}

N_TRIALS = 15
SEARCH_EPOCHS = 30       # shorter budget per trial, just to rank configs
SEARCH_PATIENCE = 6


def sample_config(rng):
    return {key: rng.choice(values) for key, values in SEARCH_SPACE.items()}


def run_search(X_train, y_train, X_val, y_val, input_dim, n_trials, rng):
    results = []
    for trial_num in range(1, n_trials + 1):
        config = sample_config(rng)
        print(f"\n--- Trial {trial_num}/{n_trials}: {config} ---")

        model, train_loss, val_loss = train(
            X_train, y_train, X_val, y_val, input_dim,
            hidden_sizes=config["hidden_sizes"],
            dropout=config["dropout"],
            learning_rate=config["learning_rate"],
            weight_decay=config["weight_decay"],
            batch_size=config["batch_size"],
            epochs=SEARCH_EPOCHS,
            patience=SEARCH_PATIENCE,
            verbose=False,
        )
        metrics = evaluate(model, X_val, y_val)
        print(f"  -> train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}, "
              f"home_mae: {metrics['home_mae']:.3f}, away_mae: {metrics['away_mae']:.3f}, "
              f"outcome_acc: {metrics['outcome_accuracy']:.4f}")

        results.append({**config, "train_loss": train_loss, "val_loss": val_loss, **metrics})

    return results


def main(data_paths, model_out, preprocessing_out, n_trials, seed):
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
    input_dim = X_train.shape[1]
    print(f"Feature matrix: {input_dim} features, {X_train.shape[0]} train rows, {X_val.shape[0]} val rows.")

    rng = random.Random(seed)
    results = run_search(X_train, y_train, X_val, y_val, input_dim, n_trials, rng)

    results_df = pd.DataFrame(results).sort_values("val_loss").reset_index(drop=True)
    print("\n" + "=" * 70)
    print("SEARCH RESULTS (best val_loss first)")
    print("=" * 70)
    print(results_df.to_string(index=False))

    best = results_df.iloc[0].to_dict()
    print(f"\nBest config found: {best}")

    print("\n" + "=" * 70)
    print(f"Retraining best config with the FULL training budget "
          f"(epochs={EPOCHS}, patience={EARLY_STOPPING_PATIENCE})...")
    print("=" * 70)

    model, final_train_loss, final_val_loss = train(
        X_train, y_train, X_val, y_val, input_dim,
        hidden_sizes=best["hidden_sizes"],
        dropout=best["dropout"],
        learning_rate=best["learning_rate"],
        weight_decay=best["weight_decay"],
        batch_size=int(best["batch_size"]),
        epochs=EPOCHS,
        patience=EARLY_STOPPING_PATIENCE,
        verbose=True,
    )
    metrics = evaluate(model, X_val, y_val)

    print("\n" + "=" * 60)
    print("FINAL RESULTS (best config, full training budget)")
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
        "input_dim": input_dim,
        "hidden_sizes": best["hidden_sizes"],
        "dropout": best["dropout"],
    }, model_out)

    with open(preprocessing_out, "wb") as f:
        pickle.dump(artifacts, f)

    print(f"\nBest model saved to {model_out}")
    print(f"Preprocessing artifacts saved to {preprocessing_out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", nargs="+", default=["machine_learning/final_dataset.csv"])
    parser.add_argument("--trials", type=int, default=N_TRIALS)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--model-out", default=MODEL_OUTPUT_PATH)
    parser.add_argument("--preprocessing-out", default=PREPROCESSING_OUTPUT_PATH)
    args = parser.parse_args()

    main(args.data, args.model_out, args.preprocessing_out, args.trials, args.seed)