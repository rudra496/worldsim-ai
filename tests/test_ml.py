"""Tests for ML models (fallback mode — no PyTorch required)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.ai.ml_models import TimeSeriesPredictor, DemandForecaster, AnomalyDetectorML
import math

def test_time_series_predictor_fallback():
    p = TimeSeriesPredictor(window_size=5)
    data = [float(i) + float(i**0.5) for i in range(30)]
    for v in data:
        p.update(v)
    metrics = p.train(data, epochs=10)
    assert metrics.get("method") == "numpy_polyfit" or "final_loss" in metrics
    preds = p.predict(5)
    assert len(preds) == 5
    assert all(isinstance(x, float) for x in preds)
    print("✓ TimeSeriesPredictor (fallback)")

def test_demand_forecaster():
    df = DemandForecaster(domain="energy", window_size=5)
    for i in range(30):
        df.update(100 + 20 * math.sin(i * 0.3))
    result = df.forecast(steps=5)
    assert "predictions" in result
    assert len(result["predictions"]) == 5
    assert result["domain"] == "energy"
    print("✓ DemandForecaster")

def test_anomaly_detector_ml():
    ad = AnomalyDetectorML(threshold=5.0, window_size=10)
    import random
    random.seed(42)
    normal = [100 + random.gauss(0, 10) for _ in range(50)]
    metrics = ad.train(normal, epochs=10)
    assert "mean" in metrics
    # Check detection works — returns dict with expected keys
    r1 = ad.detect(105.0, tick=0)
    assert "is_anomaly" in r1
    assert "score" in r1
    # Clearly anomalous value should be detected
    r2 = ad.detect(10000.0, tick=1)
    assert r2["is_anomaly"]
    print("✓ AnomalyDetectorML")

def test_predictor_save_load(tmp_path=None):
    import tempfile
    p = TimeSeriesPredictor(window_size=5)
    for i in range(20):
        p.update(float(i))
    p.train(epochs=5)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        path = f.name
    try:
        p.save(path)
        p2 = TimeSeriesPredictor(window_size=5)
        p2.load(path)
        assert len(p2._history) > 0
        print("✓ TimeSeriesPredictor save/load")
    finally:
        os.unlink(path)

if __name__ == "__main__":
    test_time_series_predictor_fallback()
    test_demand_forecaster()
    test_anomaly_detector_ml()
    test_predictor_save_load()
    print("\n✅ All ML tests passed!")
