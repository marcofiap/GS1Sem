import pytest
from unittest.mock import MagicMock, patch
from src.model.predict import WaterQualityPredictor


@pytest.fixture
def predictor(mocker):
    """Fixture para criar um preditor instanciado."""
    predictor = WaterQualityPredictor()
    predictor.processor = mocker.MagicMock()
    return predictor


def test_load_config(mocker, predictor):
    """Testa se o arquivo de configuração é carregado corretamente."""
    mock_yaml = mocker.patch("src.model.predict.yaml.safe_load", return_value={'ml': {'model_path': 'model.pkl'}})
    with patch("builtins.open", mocker.mock_open(read_data="dummy")):
        predictor._load_config()
    assert predictor.model_path.name == "model.pkl"
    mock_yaml.assert_called_once()
