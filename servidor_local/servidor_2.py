from flask import Flask, request, jsonify
# Não precisaremos mais de 'oracledb' ou 'datetime' diretamente aqui,
# pois o controller cuidará disso.
# import oracledb
# from datetime import datetime

import sys
import os

# --- IMPORTANTE: Ajuste de Caminho para importar o Controller ---
# Esta parte é crucial e depende de onde o 'servidor.py' está em relação
# à pasta 'GS1Sem-machine-python'.
#
# Exemplo 1: Se 'servidor.py' está DENTRO de 'GS1Sem-machine-python':
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
#
# Exemplo 2: Se 'servidor.py' está UM NÍVEL ACIMA de 'GS1Sem-machine-python'
# e 'GS1Sem-machine-python' é um subdiretório:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'GS1Sem-machine-python')))
# Exemplo 3: Se 'servidor.py' e a pasta 'GS1Sem-machine-python' estão no mesmo diretório:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'GS1Sem-machine-python'))) # Supondo que servidor.py está em servidor_local e GS1... está um nível acima

# Verifique se o caminho está correto imprimindo-o e testando o import
print("Sys.path modificado:", sys.path)

try:
    from src.api.controller import get_controller
    from src.utils.logging import setup_logging # Importar para configurar o logging do sistema de ML
except ImportError as e:
    print(f"ERRO CRÍTICO: Não foi possível importar o controller do sistema de ML. Verifique o sys.path.")
    print(f"Detalhes do erro: {e}")
    print("Verifique se a estrutura de pastas está correta e se os arquivos __init__.py existem onde necessário.")
    sys.exit(1) # Sai se não conseguir importar

app = Flask(__name__)

# Configurar o logging do sistema de ML uma vez
try:
    setup_logging()
    print("Logging do sistema de ML configurado.")
except FileNotFoundError:
    print("AVISO: config.yaml não encontrado para o setup_logging. O logging pode não funcionar como esperado.")
except Exception as e:
    print(f"AVISO: Erro ao configurar logging do sistema de ML: {e}")


# Obtém a instância global do controller do sistema de ML
try:
    water_ml_controller = get_controller()
    print("Instância do WaterQualityController obtida com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível obter a instância do WaterQualityController: {e}")
    print("Verifique se o config.yaml e o modelo .pkl estão nos caminhos corretos e se o Oracle DB está acessível pelo controller.")
    sys.exit(1)


# Não precisamos mais das funções de banco de dados e simulação de ML aqui,
# pois o controller e o repositório do sistema de ML cuidarão disso.
# As funções conectar_db, criar_tabela_se_nao_existir, inserir_dados_agua,
# simular_predicao_ml SERÃO REMOVIDAS ou comentadas, pois essa lógica
# agora está no sistema de ML (controller.py, db.py, predict.py).

@app.route('/data', methods=['GET']) # Mantém o endpoint que o ESP32 está usando
def receive_data_from_esp32():
    try:
        # Parâmetros que o ESP32 está enviando (main.cpp)
        # String getData = serverName + "?chlorine=" + String(chlorineValue) +
        #                "&turbidity=" + String(turbidityValue) +
        #                "&conductivity=" + String(conductivityValue) +
        #                "&ph=" + String(phValue);

        ph_str = request.args.get('ph')
        turbidity_str = request.args.get('turbidity')
        # O ESP32 envia 'chlorine', mas o controller pode esperar 'chloramines'
        # Vamos pegar 'chlorine' e passar como 'chloramines' se for o caso,
        # ou ajustar o controller/processor para aceitar 'chlorine'.
        # Por agora, vamos assumir que 'chlorine' do ESP32 refere-se a 'chloramines'
        # para o modelo de ML. Se forem coisas diferentes, isso precisa ser tratado.
        chlorine_as_chloramines_str = request.args.get('chlorine') # ESP32 envia 'chlorine'
        conductivity_str = request.args.get('conductivity') # ESP32 envia 'conductivity'

        # Verificação de parâmetros essenciais para o controller.py
        # O controller.ingest_reading espera um dicionário.
        # O método predictor.predict_from_sensor_data usa o processor,
        # que por sua vez usa self.feature_columns de data_processor.py:
        # ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
        #  'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']
        #
        # O ESP32 envia: ph, turbidity, chlorine, conductivity.
        # O controller.py no método ingest_reading espera (pelo menos):
        # {'ph': float, 'turbidity': float, 'chloramines': float}

        if None in [ph_str, turbidity_str, chlorine_as_chloramines_str]:
            return "Erro: Parâmetros ausentes (ph, turbidity, chlorine são esperados do ESP32)", 400

        ph = float(ph_str)
        turbidity = float(turbidity_str)
        chloramines = float(chlorine_as_chloramines_str) # Assumindo que 'chlorine' do ESP é 'chloramines'
        conductivity = float(conductivity_str) if conductivity_str is not None else 0.0 # Lidar com condutividade opcional

        print("Dados Recebidos do ESP32 (via servidor.py):")
        print(f"  pH: {ph}")
        print(f"  Turbidez: {turbidity}")
        print(f"  Cloraminas (do ESP32 'chlorine'): {chloramines}")
        print(f"  Condutividade: {conductivity}")


        # --- Interação com o Sistema de ML ---
        # Os dados precisam estar no formato que o `WaterDataProcessor` espera
        # ou que o `predict_from_sensor_data` espera.
        # O `predict_from_sensor_data` usa `processor.process_sensor_reading`,
        # que tenta preencher features faltantes com 0.0 se não estiverem no dicionário.
        # As features principais que o controller usa no `Reading` e na lógica de alerta são:
        # ph, turbidity, chloramines.
        sensor_data_for_ml = {
            "ph": ph,
            "turbidity": turbidity,
            "chloramines": chloramines, # Passando o valor de 'chlorine' do ESP32 como 'chloramines'
            "conductivity": conductivity
            # Se o seu modelo treinado e o WaterDataProcessor usarem OUTRAS features
            # (Hardness, Solids, Sulfate, Organic_carbon, Trihalomethanes),
            # você precisaria:
            # 1. Enviar esses dados do ESP32 (se tiver os sensores).
            # 2. Ou o `WaterDataProcessor` no método `process_sensor_reading`
            #    precisa lidar com a ausência delas (ele já tenta colocar 0.0).
            #    A precisão da predição será afetada se features importantes estiverem faltando.
        }

        # Chamar o controller do sistema de ML
        print(f"Enviando para o WaterQualityController: {sensor_data_for_ml}")
        resultado_ingestao_ml = water_ml_controller.ingest_reading(sensor_data_for_ml)
        print(f"Resultado do WaterQualityController: {resultado_ingestao_ml}")


        if resultado_ingestao_ml.get('success'):
            # O ESP32 espera "POTAVEL", "NAO_POTAVEL", ou "SUSPEITA"
            # O `controller.py` retorna um dicionário em `prediction_result` que tem `potability_label`
            predicao_label = resultado_ingestao_ml.get('prediction', {}).get('potability_label', 'ERRO_NA_PREDICAO')

            # O seu ESP32 (main.cpp) trata "POTAVEL", "SUSPEITA", "NAO_POTAVEL".
            # O `controller.py` retorna 'POTAVEL' ou 'NAO_POTAVEL'.
            # Se você quiser o "SUSPEITA", a lógica no `controller.py` ou `predict.py`
            # (especificamente `_determine_risk_level` ou a lógica de predição) precisaria ser ajustada
            # para gerar esse terceiro estado, ou você pode adaptar aqui.
            # Por enquanto, vamos retornar o que o controller fornece.
            # Se o ESP32 usa a predição "SUSPEITA", você precisará mapear.

            print(f"Predição do Sistema de ML: {predicao_label}")
            # Retorna apenas o rótulo da predição para o ESP32 como texto plano
            return predicao_label, 200
        else:
            error_message = resultado_ingestao_ml.get('message', 'Erro desconhecido ao processar no sistema de ML')
            print(f"Falha ao processar no sistema de ML: {error_message}")
            return jsonify({"sucesso": False, "mensagem": error_message}), 500

    except ValueError:
        print("Erro: Parâmetros inválidos recebidos (devem ser números).")
        return "Erro: Parâmetros inválidos (devem ser números).", 400
    except Exception as e:
        # Logar o erro 'e'
        error_msg = f"Erro interno inesperado no servidor Flask: {str(e)}"
        print(error_msg)
        # Considerar logar o traceback completo aqui para depuração
        import traceback
        traceback.print_exc()
        return f"Erro interno no servidor: {str(e)}", 500

# A rota /get_all_data pode ser mantida se você quiser uma forma simples de ver
# os dados diretamente deste servidor, mas idealmente, a interface Streamlit
# (`app.py`) já faz isso de forma mais completa através do controller.
# Se mantiver, ela deve chamar o controller também.
@app.route('/get_all_data', methods=['GET'])
def get_all_data_from_ml_db():
    """Lista todas as leituras usando o controller do sistema de ML."""
    try:
        # O controller.get_readings() já retorna uma lista de dicionários formatados.
        leituras = water_ml_controller.get_readings(limit=100) # Pega as últimas 100
        return jsonify(leituras)
    except Exception as e:
        error_msg = f"Erro ao buscar dados via controller: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    # Certifique-se de que o host é '0.0.0.0' para ser acessível na rede local
    # pelo ESP32. A porta 8000 é a que o ESP32 está usando.
    print("Iniciando servidor Flask para interface com ESP32 e Sistema de ML...")
    app.run(host='0.0.0.0', port=8000, debug=True) # debug=True é útil para desenvolvimento
    print("Servidor Flask rodando em http://0.0.0.0:8000")