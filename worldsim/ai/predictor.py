"""Prediction models and anomaly detection."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np


class SimplePredictor:
    """
    Statistical predictor using moving average and linear regression.

    Lightweight — no PyTorch dependency needed.
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self._history: List[float] = []

    def update(self, value: float) -> None:
        self._history.append(value)
        if len(self._history) > 10000:
            self._history = self._history[-10000:]

    def predict_next(self, method: str = "linear") -> float:
        if len(self._history) < 2:
            return self._history[-1] if self._history else 0.0

        if method == "moving_average":
            window = self._history[-self.window_size:]
            return float(np.mean(window))
        elif method == "linear":
            n = min(len(self._history), self.window_size * 3)
            y = np.array(self._history[-n:])
            x = np.arange(n, dtype=float)
            coeffs = np.polyfit(x, y, 1)
            return float(np.polyval(coeffs, n))
        elif method == "exponential":
            alpha = 2.0 / (self.window_size + 1)
            result = self._history[0]
            for val in self._history[1:]:
                result = alpha * val + (1 - alpha) * result
            return float(result)
        else:
            return float(np.mean(self._history[-self.window_size:]))

    def predict_range(self, steps: int = 5) -> List[float]:
        """Predict multiple future values."""
        predictions = []
        for _ in range(steps):
            pred = self.predict_next("linear")
            predictions.append(pred)
            self._history.append(pred)
        # Remove the fake entries
        self._history = self._history[:-steps]
        return predictions

    def step(self, tick: int, state: Dict[str, Any], env_state: Dict[str, Any],
             agent_states: Dict[str, Any]) -> Dict[str, Any]:
        """AI module interface — called each tick."""
        energy = state.get("total_energy_consumption", 0)
        self.update(energy)
        prediction = self.predict_next()
        return {
            "predicted_energy": prediction,
            "method": "linear_regression",
            "history_length": len(self._history),
        }


class AnomalyDetector:
    """
    Simple statistical anomaly detection.

    Flags values that deviate significantly from the moving average.
    """

    def __init__(self, window_size: int = 20, threshold_std: float = 2.0):
        self.window_size = window_size
        self.threshold_std = threshold_std
        self._values: List[float] = []
        self._anomalies: List[Dict[str, Any]] = []

    def check(self, value: float, tick: int = 0) -> Dict[str, Any]:
        """Check if a value is anomalous."""
        self._values.append(value)

        if len(self._values) < self.window_size:
            return {"is_anomaly": False, "value": value, "tick": tick}

        window = self._values[-self.window_size:]
        mean = float(np.mean(window))
        std = float(np.std(window))

        if std == 0:
            is_anomaly = value != mean
        else:
            z_score = abs(value - mean) / std
            is_anomaly = z_score > self.threshold_std

        result = {
            "is_anomaly": is_anomaly,
            "value": value,
            "expected": mean,
            "std": std,
            "z_score": abs(value - mean) / std if std > 0 else 0.0,
            "tick": tick,
        }

        if is_anomaly:
            self._anomalies.append(result)

        return result

    def get_anomalies(self) -> List[Dict[str, Any]]:
        return list(self._anomalies)

    def reset(self) -> None:
        self._values.clear()
        self._anomalies.clear()
