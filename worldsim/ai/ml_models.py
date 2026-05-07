"""ML-based prediction models with PyTorch (optional) and NumPy fallback."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

HAS_TORCH = False
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    pass


class TimeSeriesPredictor:
    """
    LSTM-based time series forecaster.
    
    Falls back to NumPy linear regression if PyTorch is not available.
    """

    def __init__(self, input_size: int = 1, hidden_size: int = 64,
                 num_layers: int = 2, window_size: int = 20,
                 device: str = "cpu"):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.window_size = window_size
        self.device = device
        self._history: List[float] = []
        self._model = None
        self._trained = False

        if HAS_TORCH:
            self._model = self._build_lstm()
            self._model.to(device)

    def _build_lstm(self) -> Any:
        """Build PyTorch LSTM model."""
        class LSTMModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers):
                super().__init__()
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                                     batch_first=True, dropout=0.1)
                self.fc = nn.Linear(hidden_size, 1)

            def forward(self, x):
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])
        
        return LSTMModel(self.input_size, self.hidden_size, self.num_layers)

    def _prepare_sequences(self, data: List[float]) -> Tuple[Any, Any]:
        """Convert data to sequences for LSTM training."""
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i:i + self.window_size])
            y.append(data[i + self.window_size])
        X = np.array(X, dtype=np.float32).reshape(-1, self.window_size, 1)
        y = np.array(y, dtype=np.float32)
        return X, y

    def update(self, value: float) -> None:
        self._history.append(value)
        if len(self._history) > 50000:
            self._history = self._history[-50000:]

    def train(self, data: Optional[List[float]] = None, epochs: int = 50,
              lr: float = 0.001) -> Dict[str, float]:
        """Train the predictor."""
        history = data or self._history
        if len(history) < self.window_size + 10:
            return {"status": "not_enough_data", "history_len": len(history)}

        X, y = self._prepare_sequences(history)
        metrics = {"samples": len(X)}

        if HAS_TORCH and self._model:
            X_t = torch.FloatTensor(X).to(self.device)
            y_t = torch.FloatTensor(y).to(self.device)
            optimizer = torch.optim.Adam(self._model.parameters(), lr=lr)
            criterion = nn.MSELoss()
            self._model.train()

            losses = []
            for epoch in range(epochs):
                optimizer.zero_grad()
                pred = self._model(X_t).squeeze()
                loss = criterion(pred, y_t)
                loss.backward()
                optimizer.step()
                losses.append(loss.item())

            self._trained = True
            self._model.eval()
            metrics["final_loss"] = losses[-1]
            metrics["min_loss"] = min(losses)
            metrics["epochs"] = epochs
        else:
            # Fallback: fit polynomial regression
            self._fit_numpy(history)
            metrics["method"] = "numpy_polyfit"
            metrics["status"] = "fallback_trained"

        return metrics

    def _fit_numpy(self, data: List[float]) -> None:
        """Fit NumPy polynomial regression as fallback."""
        if len(data) < 3:
            return
        self._np_coeffs = np.polyfit(range(len(data)), data, min(3, len(data) - 1))

    def predict(self, future_steps: int = 5) -> List[float]:
        """Predict future values."""
        if len(self._history) < self.window_size:
            last = self._history[-1] if self._history else 0.0
            return [last] * future_steps

        if HAS_TORCH and self._model and self._trained:
            return self._predict_torch(future_steps)
        return self._predict_numpy(future_steps)

    def _predict_torch(self, steps: int) -> List[float]:
        """PyTorch LSTM prediction."""
        self._model.eval()
        window = np.array(self._history[-self.window_size:], dtype=np.float32)
        window = window.reshape(1, self.window_size, 1)
        x = torch.FloatTensor(window).to(self.device)
        
        with torch.no_grad():
            predictions = []
            current = x
            for _ in range(steps):
                pred = self._model(current).item()
                predictions.append(pred)
                # Shift window
                current = torch.cat([current[:, 1:, :], 
                                     torch.FloatTensor([[pred]]).unsqueeze(0).to(self.device)], dim=1)
            return predictions

    def _predict_numpy(self, steps: int) -> List[float]:
        """NumPy polynomial prediction."""
        if not hasattr(self, '_np_coeffs'):
            return [self._history[-1]] * steps
        n = len(self._history)
        predictions = []
        for i in range(steps):
            val = float(np.polyval(self._np_coeffs, n + i))
            predictions.append(max(0, val))
        return predictions

    def predict_next(self) -> float:
        return self.predict(1)[0]

    def save(self, path: str) -> None:
        """Save model to disk."""
        data = {
            "window_size": self.window_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "history": self._history[-1000:],
            "trained": self._trained,
        }
        if HAS_TORCH and self._model and self._trained:
            data["state_dict"] = {k: v.tolist() for k, v in self._model.state_dict().items()}
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(data))

    def load(self, path: str) -> None:
        """Load model from disk."""
        data = json.loads(Path(path).read_text())
        self._history = data.get("history", [])
        self._trained = data.get("trained", False)
        if HAS_TORCH and self._model and "state_dict" in data:
            state = {k: torch.FloatTensor(v) for k, v in data["state_dict"].items()}
            self._model.load_state_dict(state)
            self._model.eval()


class DemandForecaster:
    """
    Domain-specific demand forecaster.
    Wraps TimeSeriesPredictor with preprocessing.
    """

    def __init__(self, domain: str = "energy", window_size: int = 20):
        self.domain = domain
        self._predictor = TimeSeriesPredictor(window_size=window_size)
        self._mean: Optional[float] = None
        self._std: Optional[float] = None
        self._buffer: List[float] = []

    def update(self, value: float) -> None:
        self._buffer.append(value)
        self._predictor.update(value)
        if len(self._buffer) > 2:
            arr = np.array(self._buffer)
            self._mean = float(np.mean(arr))
            self._std = float(np.std(arr)) + 1e-8

    def train(self, epochs: int = 30) -> Dict[str, Any]:
        normalized = self._normalize(self._buffer)
        return self._predictor.train(data=normalized, epochs=epochs)

    def forecast(self, steps: int = 10) -> Dict[str, Any]:
        if len(self._buffer) < 5:
            return {"predictions": [0.0] * steps, "domain": self.domain}
        normalized = self._normalize(self._buffer)
        self._predictor.train(data=normalized, epochs=20)
        preds = self._predictor.predict(steps)
        denorm = self._denormalize(preds)
        return {
            "domain": self.domain,
            "predictions": denorm,
            "current_mean": self._mean,
            "current_std": self._std,
            "confidence": max(0, 1.0 - (self._std / (abs(self._mean) + 1e-8))),
        }

    def _normalize(self, data: List[float]) -> List[float]:
        if not self._mean or not self._std:
            return data
        return [(x - self._mean) / self._std for x in data]

    def _denormalize(self, data: List[float]) -> List[float]:
        if not self._mean or not self._std:
            return data
        return [x * self._std + self._mean for x in data]

    def step(self, tick: int, state: Dict[str, Any], env_state: Dict[str, Any],
             agent_states: Dict[str, Any]) -> Dict[str, Any]:
        key = f"{self.domain}_consumption"
        value = state.get(key, state.get("total_energy_consumption", 0))
        self.update(value)
        forecast = self.forecast(steps=5)
        return {f"{self.domain}_forecast": forecast}


class AnomalyDetectorML:
    """
    Autoencoder-based anomaly detection with NumPy fallback.
    """

    def __init__(self, threshold: float = 2.0, window_size: int = 30):
        self.threshold = threshold
        self.window_size = window_size
        self._values: List[float] = []
        self._anomalies: List[Dict[str, Any]] = []
        self._mean: float = 0.0
        self._std: float = 1.0
        self._autoencoder: Optional[Any] = None
        self._trained = False

        if HAS_TORCH:
            self._autoencoder = self._build_autoencoder()

    def _build_autoencoder(self) -> Any:
        class Autoencoder(nn.Module):
            def __init__(self, input_size):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_size, 16), nn.ReLU(),
                    nn.Linear(16, 8), nn.ReLU(),
                    nn.Linear(8, 4),
                )
                self.decoder = nn.Sequential(
                    nn.Linear(4, 8), nn.ReLU(),
                    nn.Linear(8, 16), nn.ReLU(),
                    nn.Linear(16, input_size),
                )
            def forward(self, x):
                return self.decoder(self.encoder(x))
        
        return Autoencoder(self.window_size)

    def train(self, normal_data: List[float], epochs: int = 50, lr: float = 0.001) -> Dict[str, Any]:
        """Train on normal data to learn expected patterns."""
        self._values = list(normal_data)
        if len(normal_data) < self.window_size + 5:
            return {"status": "not_enough_data"}

        # Update statistics
        self._mean = float(np.mean(normal_data))
        self._std = float(np.std(normal_data)) + 1e-8
        metrics = {"mean": self._mean, "std": self._std, "samples": len(normal_data)}

        if HAS_TORCH and self._autoencoder:
            # Prepare windows
            windows = []
            for i in range(len(normal_data) - self.window_size):
                w = normal_data[i:i + self.window_size]
                windows.append(w)
            X = torch.FloatTensor(windows)
            
            optimizer = torch.optim.Adam(self._autoencoder.parameters(), lr=lr)
            criterion = nn.MSELoss()
            self._autoencoder.train()
            
            losses = []
            for epoch in range(epochs):
                optimizer.zero_grad()
                recon = self._autoencoder(X)
                loss = criterion(recon, X)
                loss.backward()
                optimizer.step()
                losses.append(loss.item())
            
            self._autoencoder.eval()
            self._trained = True
            metrics["reconstruction_loss"] = losses[-1]
            metrics["method"] = "autoencoder"
        else:
            metrics["method"] = "statistical"

        return metrics

    def detect(self, value: float, tick: int = 0) -> Dict[str, Any]:
        """Check if a value is anomalous."""
        self._values.append(value)
        is_anomaly = False
        score = 0.0

        # Statistical check
        if self._std > 0:
            z_score = abs(value - self._mean) / self._std
            is_anomaly = z_score > self.threshold
            score = z_score

        # Autoencoder check (if trained)
        if HAS_TORCH and self._autoencoder and self._trained:
            if len(self._values) >= self.window_size:
                window = torch.FloatTensor([self._values[-self.window_size:]])
                with torch.no_grad():
                    recon = self._autoencoder(window)
                    ae_loss = float(torch.mean((window - recon) ** 2))
                if ae_loss > self.threshold:
                    is_anomaly = True
                    score = max(score, ae_loss)

        result = {
            "is_anomaly": is_anomaly,
            "value": value,
            "score": round(score, 4),
            "tick": tick,
        }
        if is_anomaly:
            self._anomalies.append(result)
        return result

    def get_anomalies(self) -> List[Dict[str, Any]]:
        return list(self._anomalies)

    def save(self, path: str) -> None:
        data = {"mean": self._mean, "std": self._std, "trained": self._trained,
                "threshold": self.threshold, "anomalies": self._anomalies[-100:]}
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(data))

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text())
        self._mean = data["mean"]; self._std = data["std"]
        self._trained = data["trained"]; self.threshold = data.get("threshold", 2.0)
        self._anomalies = data.get("anomalies", [])
