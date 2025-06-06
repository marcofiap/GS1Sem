import pytest
from unittest.mock import MagicMock, patch

from src.model import WaterQualityPredictor


@pytest.fixture
def predictor():
    """Fixture para criar um preditor instanciado."""
    return WaterQualityPredictor()


def test_predict(mocker, predictor):
    """Testa a funcionalidade de predição usando o modelo carregado."""
    model_mock = MagicMock()
    model_mock.predict.return_value = [1]
    model_mock.predict_proba.return_value = [[0.3, 0.7]]

    predictor.model = model_mock
    predictor.is_loaded = True

    features = [7.0, 100.0, 2000.0, 1.0, 300.0, 400.0, 10.0, 80.0, 3.0]
    prediction = predictor.predict(features)

    assert prediction is True
    model_mock.predict.assert_called_once()
    model_mock.predict_proba.assert_called_once()


def test_predict_from_sensor_data(mocker, predictor):
    """Testa a predição com dados de sensores."""
    predictor.processor = MagicMock()
    predictor.processor.process_sensor_reading.return_value = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]]
    predictor.model = MagicMock()
    predictor.model.predict.return_value = [0]
    predictor.model.predict_proba.return_value = [[0.8, 0.2]]
    predictor.is_loaded = True

    sensor_data = {
        "ph": 6.0,
        "turbidity": 4.0,
        "chloramines": 0.8,
        "conductivity": 300.0
    }

    result = predictor.predict_from_sensor_data(sensor_data)
    assert result['is_potable'] is False
    assert result['potability_label'] == "NAO_POTAVEL"