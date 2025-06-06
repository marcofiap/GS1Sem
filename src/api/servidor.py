from flask import Flask, request, jsonify

from src.api import get_controller

app = Flask(__name__)

# *** Configurações do Banco de Dados Oracle ***
DB_USER = "system"  # Substitua pelo seu nome de usuário Oracle
DB_PASSWORD = "system"  # Substitua pela sua senha Oracle
DB_DSN = "localhost:1521/xe"  # Substitua pela sua string de conexão DSN (e.g., "localhost/XEPDB1" ou "your_oracle_host:1521/your_service_name")

@app.route('/data', methods=['GET'])
def receive_data():
    try:
        data = request.args
        print(f"Dados recebidos: {data}")  # Log para debug

        reading_data = {
            'ph': float(data.get('ph', 7.0)),
            'turbidity': float(data.get('turbidity', 4.0)),
            'chloramines': float(data.get('chlorine', 0.0))
        }
        print(f"Dados processados: {reading_data}")  # Log para debug

        controller = get_controller()
        result = controller.ingest_reading(reading_data)

        return result['prediction']['potability_label'], 200

    except Exception as e:
        print(f"Erro detalhado: {str(e)}")  # Log detalhado do erro
        return f"Erro interno no servidor: {str(e)}", 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    print("Servidor Flask rodando em http://0.0.0.0:8000")