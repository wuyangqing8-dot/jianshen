"""Optional expert-score model adapter; rule scoring remains available without it.

Only load a model trained on consented, expert-labelled participant data.
The training artifact is produced by evaluation/train_random_forest.py.
"""
from pathlib import Path
import math


class ExpertScoreModel:
    def __init__(self, path):
        import joblib  # Optional dependency, installed only for the research model.

        artifact = joblib.load(Path(path))
        if not isinstance(artifact, dict) or not artifact.get('features') or not hasattr(artifact.get('model'), 'predict'):
            raise ValueError('Invalid expert-score artifact')
        self.model = artifact['model']
        self.features = tuple(artifact['features'])

    def predict(self, features):
        """Return None when a required measurement is unavailable."""
        row = [features.get(name) for name in self.features]
        if any(v is None or not isinstance(v, (int, float)) or not math.isfinite(v) for v in row):
            return None
        return max(0., min(100., float(self.model.predict([row])[0])))
