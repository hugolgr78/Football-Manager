"""
predictor.py

Class-based interface for scoring a single match from its player-attribute
row. Loads the trained model + preprocessing artifacts (from train_model.py
/ tune_model.py) once per distinct (model_path, preprocessing_path) pair and
reuses them across instances, so predicting many rows in a loop doesn't
reload the model from disk every time.

Usage:
    from predictor import MatchScorePredictor

    predictor = MatchScorePredictor(row)          # row: dict, pd.Series, or 1-row DataFrame
    home_score, away_score = predictor.predict()

    # Everything predict() computed is also kept as attributes:
    predictor.home_expected_goals   # e.g. 1.84 (raw Poisson rate, before rounding)
    predictor.away_expected_goals   # e.g. 1.12
    predictor.home_score_predicted  # e.g. 2   (rounded)
    predictor.away_score_predicted  # e.g. 1
    predictor.predicted_outcome     # "home_win" / "draw" / "away_win"

    # If the row you passed in also had home_score/away_score columns
    # (e.g. you're checking the model against a known result), the actual
    # result and how far off the prediction was are captured too:
    predictor.actual_home_score
    predictor.actual_away_score
    predictor.actual_outcome
    predictor.home_error            # predicted - actual, home side
    predictor.away_error            # predicted - actual, away side

Example (predicting a batch of rows from a CSV, reusing the loaded model):
    import pandas as pd
    df = pd.read_csv("machine_learning/final_dataset.csv")
    for _, row in df.head(10).iterrows():
        p = MatchScorePredictor(row)
        p.predict()
        print(p)
"""

import pickle

import pandas as pd
import torch

from train_model import (
    MatchScoreNet, build_features, derive_outcome,
    MODEL_OUTPUT_PATH, PREPROCESSING_OUTPUT_PATH, DEVICE,
)

OUTCOME_LABELS = {0: "home_win", 1: "draw", 2: "away_win"}


class MatchScorePredictor:
    # Cache of loaded (model, artifacts) pairs, keyed by the file paths they
    # came from - shared across every instance, so creating many predictors
    # against the same model doesn't re-read it from disk each time.
    _cache = {}

    def __init__(self, row, model_path=MODEL_OUTPUT_PATH, preprocessing_path=PREPROCESSING_OUTPUT_PATH):
        """
        row: the observed data for one match - a dict, a pandas Series, or a
        one-row DataFrame - with the same columns as the training data
        (home_formation, away_formation, and all the player attribute
        columns). If home_score/away_score are also present in row, they're
        kept as the "actual" result for comparison, but have no effect on
        the prediction itself (build_features always drops them).
        """
        self.row_df = self._normalize_row(row)
        self.model_path = model_path
        self.preprocessing_path = preprocessing_path
        self.model, self.artifacts = self._load(model_path, preprocessing_path)

        # Populated by predict()
        self.home_expected_goals = None
        self.away_expected_goals = None
        self.home_score_predicted = None
        self.away_score_predicted = None
        self.predicted_outcome = None

        # Populated now, from the row itself, if it has a known result
        self.actual_home_score = None
        self.actual_away_score = None
        self.actual_outcome = None
        self._extract_actual_result()

        # Populated by predict(), only if an actual result was available
        self.home_error = None
        self.away_error = None

    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_row(row):
        if isinstance(row, pd.DataFrame):
            return row.iloc[[0]].reset_index(drop=True)
        if isinstance(row, pd.Series):
            return row.to_frame().T.reset_index(drop=True)
        if isinstance(row, dict):
            return pd.DataFrame([row])
        raise TypeError(f"row must be a dict, pandas Series, or one-row DataFrame, got {type(row)}")

    @classmethod
    def _load(cls, model_path, preprocessing_path):
        key = (str(model_path), str(preprocessing_path))
        if key not in cls._cache:
            checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=False)
            model = MatchScoreNet(
                input_dim=checkpoint["input_dim"],
                hidden_sizes=checkpoint["hidden_sizes"],
                dropout=checkpoint["dropout"],
            ).to(DEVICE)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()

            with open(preprocessing_path, "rb") as f:
                artifacts = pickle.load(f)

            cls._cache[key] = (model, artifacts)
        return cls._cache[key]

    def _extract_actual_result(self):
        cols = self.row_df.columns
        if "home_score" not in cols or "away_score" not in cols:
            return
        try:
            self.actual_home_score = float(self.row_df["home_score"].iloc[0])
            self.actual_away_score = float(self.row_df["away_score"].iloc[0])
            self.actual_outcome = OUTCOME_LABELS[
                int(derive_outcome(self.actual_home_score, self.actual_away_score))
            ]
        except (TypeError, ValueError):
            # score present but unparseable (blank/NaN) - leave as None
            pass

    # ------------------------------------------------------------------ #
    def predict(self):
        """Runs the model on this instance's row and returns (home_score,
        away_score) as rounded integers. Also stores every intermediate
        result as an attribute on this instance - see the module docstring."""
        X, _ = build_features(
            self.row_df,
            formation_categories=self.artifacts["formation_categories"],
            feature_columns=self.artifacts["feature_columns"],
            imputer_medians=self.artifacts["imputer_medians"],
            scaler=self.artifacts["scaler"],
            fit=False,
        )
        X_t = torch.tensor(X, dtype=torch.float32).to(DEVICE)

        with torch.no_grad():
            log_rates = self.model(X_t)
            rates = torch.exp(log_rates).cpu().numpy()[0]

        self.home_expected_goals = float(rates[0])
        self.away_expected_goals = float(rates[1])
        self.home_score_predicted = round(self.home_expected_goals)
        self.away_score_predicted = round(self.away_expected_goals)

        # Outcome derived from the raw rates (not the rounded score) - more
        # principled, same approach used in train_model.py's evaluation.
        self.predicted_outcome = OUTCOME_LABELS[
            int(derive_outcome(self.home_expected_goals, self.away_expected_goals))
        ]

        if self.actual_home_score is not None:
            self.home_error = self.home_score_predicted - self.actual_home_score
            self.away_error = self.away_score_predicted - self.actual_away_score

        return self.home_score_predicted, self.away_score_predicted

    # ------------------------------------------------------------------ #
    def __repr__(self):
        if self.home_expected_goals is None:
            return "MatchScorePredictor(not yet predicted - call .predict())"

        parts = [
            f"predicted={self.home_score_predicted}-{self.away_score_predicted}",
            f"(expected goals {self.home_expected_goals:.2f}-{self.away_expected_goals:.2f})",
            f"outcome={self.predicted_outcome}",
        ]
        if self.actual_home_score is not None:
            parts.append(f"actual={self.actual_home_score:.0f}-{self.actual_away_score:.0f}")
            parts.append(f"outcome={self.actual_outcome}")
        return "MatchScorePredictor(" + ", ".join(parts) + ")"