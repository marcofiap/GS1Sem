#!/usr/bin/env python3
####################################
##### Arquivo: servidor_wokwi.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

"""
Servidor Flask para receber dados do ESP32/Wokwi e integrar com o sistema de ML.
"""

import sys
import os
from flask import Flask, request, jsonify
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.api.controller import get_controller
    from src.utils.logging import setup_logging, get_logger
    print("✅ Módulos do sistema ML importados com sucesso")
except ImportError as e:
    print(f"❌ ERRO: Não foi possível importar módulos: {e}")
    print("💡 Certifique-se de que está na pasta raiz do projeto")
    sys.exit(1)

# Configurar logging
setup_logging()
logger = get_logger(__name__)

app = Flask(__name__)

# Obter controller global
try:
    controller = get_controller()
    logger.info("Controller ML inicializado com sucesso")
    print("✅ Sistema de ML conectado e pronto")
except Exception as e:
    logger.error(f"Erro ao inicializar controller: {e}")
    print(f"❌ ERRO: Falha ao conectar sistema ML: {e}")
    sys.exit(1)

def mapear_dados_esp32(ph, turbidity, chlorine, conductivity):
    """
    Mapeia e valida dados recebidos do ESP32 para o formato esperado pelo ML.
    """
    try:
        # Validar ranges esperados
        if not (0 <= ph <= 14):
            logger.warning(f"pH fora do range esperado: {ph}")
        
        if turbidity < 0 or turbidity > 1000:
            logger.warning(f"Turbidez fora do range esperado: {turbidity}")
        
        if chlorine < 0 or chlorine > 10:
            logger.warning(f"Cloro fora do range esperado: {chlorine}")
            
        if conductivity < 0 or conductivity > 3000:
            logger.warning(f"Condutividade fora do range esperado: {conductivity}")

        # Mapear para formato do ML (usar chlorine como chloramines)
        sensor_data = {
            'ph': float(ph),
            'turbidity': float(turbidity),
            'chloramines': float(chlorine),  # ESP32 envia 'chlorine', ML usa 'chloramines'
            'conductivity': float(conductivity)
        }
        
        return sensor_data, True
        
    except Exception as e:
        logger.error(f"Erro ao mapear dados: {e}")
        return {}, False

@app.route('/data', methods=['GET'])
def receive_esp32_data():
    """
    Endpoint principal para receber dados do ESP32.
    Esperado: GET /data?ph=X&turbidity=Y&chlorine=Z&conductivity=W
    Retorna: String com predição ("POTAVEL", "NAO_POTAVEL")
    """
    try:
        # Capturar parâmetros do ESP32
        ph_str = request.args.get('ph')
        turbidity_str = request.args.get('turbidity')
        chlorine_str = request.args.get('chlorine')
        conductivity_str = request.args.get('conductivity')
        
        # Validar parâmetros obrigatórios
        if None in [ph_str, turbidity_str, chlorine_str]:
            error_msg = "Parâmetros obrigatórios ausentes: ph, turbidity, chlorine"
            logger.error(error_msg)
            return f"ERRO: {error_msg}", 400
        
        # Converter para float
        try:
            ph = float(ph_str)
            turbidity = float(turbidity_str)
            chlorine = float(chlorine_str)
            conductivity = float(conductivity_str) if conductivity_str else 0.0
        except ValueError as e:
            error_msg = f"Parâmetros inválidos (devem ser números): {e}"
            logger.error(error_msg)
            return f"ERRO: {error_msg}", 400
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        logger.info(f"[{timestamp}] Dados recebidos do ESP32 - pH:{ph}, Turbidez:{turbidity}, Cloro:{chlorine}, Condutividade:{conductivity}")
        
        # Mapear dados para formato ML
        sensor_data, mapping_ok = mapear_dados_esp32(ph, turbidity, chlorine, conductivity)
        if not mapping_ok:
            return "ERRO: Falha no mapeamento dos dados", 400
        
        # Processar com sistema ML
        logger.info(f"Enviando para sistema ML: {sensor_data}")
        resultado = controller.ingest_reading(sensor_data)
        
        if resultado.get('success'):
            # Extrair predição
            prediction_info = resultado.get('prediction', {})
            potability_label = prediction_info.get('potability_label', 'ERRO')
            confidence = prediction_info.get('confidence', 0.0)
            risk_level = prediction_info.get('risk_level', 'UNKNOWN')
            
            logger.info(f"✅ Predição: {potability_label} (Confiança: {confidence:.1%}, Risco: {risk_level})")
            
            # Verificar se dados foram salvos corretamente
            reading_saved = resultado.get('reading_saved', False)
            if reading_saved:
                logger.info("💾 Dados salvos no banco Oracle com sucesso")
            else:
                logger.warning("⚠️ Falha ao salvar dados no banco Oracle")
            
            # Retornar predição para ESP32 (formato esperado)
            return potability_label, 200
            
        else:
            error_message = resultado.get('message', 'Erro desconhecido no sistema ML')
            logger.error(f"❌ Falha no sistema ML: {error_message}")
            return f"ERRO_ML: {error_message}", 500
            
    except Exception as e:
        error_msg = f"Erro interno no servidor: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return f"ERRO_SERVIDOR: {str(e)}", 500

@app.route('/status', methods=['GET'])
def server_status():
    """
    Endpoint para verificar status do servidor e sistema ML.
    """
    try:
        # Testar conexão com ML
        stats = controller.get_statistics()
        
        status_info = {
            'servidor': 'ONLINE',
            'sistema_ml': 'CONECTADO',
            'banco_oracle': 'CONECTADO' if stats else 'ERRO',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estatisticas': stats,
            'versao': '1.0.0'
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({
            'servidor': 'ONLINE',
            'sistema_ml': 'ERRO',
            'erro': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/historico', methods=['GET'])
def get_historico():
    """
    Endpoint para obter histórico de leituras.
    """
    try:
        limit = int(request.args.get('limit', 50))
        leituras = controller.get_readings(limit=limit)
        
        return jsonify({
            'success': True,
            'total': len(leituras),
            'leituras': leituras
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/alertas', methods=['GET'])
def get_alertas():
    """
    Endpoint para obter alertas do sistema.
    """
    try:
        limit = int(request.args.get('limit', 20))
        alertas = controller.get_alerts(limit=limit)
        
        return jsonify({
            'success': True,
            'total': len(alertas),
            'alertas': alertas
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """
    Endpoint de teste para validar funcionamento.
    """
    test_data = {
        'ph': 7.2,
        'turbidity': 3.5,
        'chlorine': 1.8,
        'conductivity': 450.0
    }
    
    return f"TESTE OK - Dados exemplo: {test_data}", 200

@app.route('/', methods=['GET'])
def home():
    """
    Página inicial com informações básicas.
    """
    info = """
    🌊 SERVIDOR WOKWI - MONITORAMENTO DE QUALIDADE DA ÁGUA
    =====================================================
    
    Endpoints disponíveis:
    
    🔗 GET /data?ph=X&turbidity=Y&chlorine=Z&conductivity=W
       - Recebe dados do ESP32 e retorna predição
    
    📊 GET /status
       - Status do servidor e sistema ML
    
    📋 GET /historico?limit=N
       - Histórico de leituras (padrão: 50)
    
    🚨 GET /alertas?limit=N
       - Alertas do sistema (padrão: 20)
    
    🧪 GET /test
       - Endpoint de teste
    
    Sistema de ML integrado ✅
    Banco Oracle conectado ✅
    """
    return info, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    print("="*60)
    print("🌊 SERVIDOR WOKWI - QUALIDADE DA ÁGUA")
    print("="*60)
    print("🚀 Iniciando servidor Flask...")
    print("🔗 Endpoints ESP32: http://0.0.0.0:8000/data")
    print("📊 Status: http://0.0.0.0:8000/status")
    print("🏠 Home: http://0.0.0.0:8000/")
    print("💡 Para parar: Ctrl+C")
    print("="*60)
    
    try:
        # Iniciar servidor
        app.run(
            host='0.0.0.0',        # Acessível de qualquer IP
            port=8000,             # Porta esperada pelo ESP32
            debug=True,            # Debug habilitado
            threaded=True          # Suporte a múltiplas requisições
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        logger.error(f"Erro crítico no servidor: {e}") 