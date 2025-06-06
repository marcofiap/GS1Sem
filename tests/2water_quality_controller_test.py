import pytest
from src.api.servidor import app


@pytest.fixture
def client():
    """Cliente de testes do Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_receive_data_success(client, mocker):
    """Testa o endpoint /data com dados válidos."""
    # Arrange
    mock_controller = mocker.patch("src.api.servidor.get_controller")
    mock_controller.return_value.ingest_reading.return_value = {
        'prediction': {'potability_label': 'POTAVEL'}
    }

    params = {
        'ph': 7.0,
        'turbidity': 4.0,
        'chlorine': 2.0
    }

    # Act
    response = client.get('/data', query_string=params)

    # Assert
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'POTAVEL'



def test_receive_data_invalid_params(client, mocker):
    """Testa o endpoint /data com parâmetros inválidos."""
    # Arrange
    invalid_params = {
        'ph': 'invalido',
        'turbidity': 4.0,
        'chlorine': 2.0
    }

    # Act
    response = client.get('/data', query_string=invalid_params)

    # Assert
    assert response.status_code == 500