import pytest
from unittest.mock import MagicMock
from datetime import datetime
from src.api.controller import WaterQualityController


@pytest.fixture
def mock_controller():
    """Mocka o controlador WaterQualityController."""
    controller = WaterQualityController()
    controller.repository = MagicMock()  # Mock do repositório
    controller.predictor = MagicMock()  # Mock do preditor
    return controller


def test_ingest_reading_success(mock_controller):
    """Testa o sucesso do método ingest_reading."""
    # Arrange
    mock_controller.predictor.predict_from_sensor_data.return_value = {
        'is_potable': True,
        'potability_label': 'POTAVEL'
    }
    mock_controller.repository.save_reading.return_value = True

    reading_data = {
        'ph': 7.0,
        'turbidity': 3.5,
        'chloramines': 1.2
    }

    # Act
    result = mock_controller.ingest_reading(reading_data)

    # Assert
    assert result['success'] is True
    assert result['prediction']['potability_label'] == 'POTAVEL'
    assert 'timestamp' in result


def test_ingest_reading_failure(mock_controller):
    """Testa falha ao salvar leitura no repositório."""
    # Arrange
    mock_controller.predictor.predict_from_sensor_data.return_value = {
        'is_potable': False,
        'potability_label': 'NAO_POTAVEL'
    }
    mock_controller.repository.save_reading.return_value = False

    reading_data = {
        'ph': 5.0,
        'turbidity': 10.0,
        'chloramines': 0.5
    }

    # Act
    result = mock_controller.ingest_reading(reading_data)

    # Assert
    assert result['success'] is False
    assert result['message'] == 'Erro ao salvar leitura'


def test_get_readings_success(mock_controller):
    """Testa a recuperação de leituras do método get_readings."""
    # Arrange
    mock_controller.repository.get_readings.return_value = [
        MagicMock(id=1, timestamp=datetime(2023, 1, 1), ph=7.5, turbidity=3.0, chloramines=1.0, potability=1)
    ]

    # Act
    result = mock_controller.get_readings()

    # Assert
    assert len(result) == 1
    assert result[0]['potability_label'] == 'POTAVEL'


def test_get_alerts_success(mock_controller):
    """Testa a recuperação de alertas do método get_alerts."""
    # Arrange
    mock_controller.repository.get_alerts.return_value = [
        MagicMock(id=1, timestamp=datetime(2023, 1, 1), ph=5.0, turbidity=120.0, chloramines=0.2)
    ]

    # Act
    result = mock_controller.get_alerts()

    # Assert
    assert len(result) == 1
    assert result[0]['severity'] == 'critica'