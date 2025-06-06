import pytest
from unittest.mock import MagicMock, patch
from src.model.train import WaterQualityModelTrainer


@pytest.fixture
def trainer(mocker):
    """Fixture para criar uma instância de treinamento configurada."""
    trainer = WaterQualityModelTrainer()
    # Mock do processador padrão
    trainer.processor = mocker.MagicMock()
    return trainer


def test_load_config(mocker, trainer):
    """Testa se o arquivo de configuração é carregado corretamente."""
    mock_yaml = mocker.patch("src.model.train.yaml.safe_load", return_value={'ml': {'model_path': 'model.pkl'}})
    with patch("builtins.open", mocker.mock_open(read_data="dummy")):
        trainer._load_config()
    assert trainer.model_path == "model.pkl"
    mock_yaml.assert_called_once()


def test_save_model(mocker, trainer):
    """Testa se o modelo treinado é salvo corretamente."""
    trainer.model = MagicMock()
    trainer.processor = MagicMock()
    trainer.model_path = "test_model_path.pkl"

    mocker.patch("src.model.train.joblib.dump")
    mocker.patch("pathlib.Path.mkdir")

    trainer.save_model()

    assert trainer.model_path == "test_model_path.pkl"