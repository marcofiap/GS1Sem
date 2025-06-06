####################################
##### Arquivo: controller.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

from datetime import datetime
from typing import Dict, List, Optional
from ..persistence.db import Reading, WaterQualityRepository
from ..model.predict import get_predictor
from ..utils.logging import get_logger

logger = get_logger(__name__)

class WaterQualityController:
    """Controller para orquestrar operações de qualidade da água."""
    
    def __init__(self):
        self.repository = WaterQualityRepository()
        self.predictor = get_predictor()
    
    def ingest_reading(self, reading_data: Dict[str, float]) -> Dict[str, any]:
        """
        Processa uma nova leitura de dados dos sensores.
        
        Args:
            reading_data: Dados dos sensores (ph, turbidity, chloramines, conductivity)
        
        Returns:
            Dict com resultado do processamento
        """
        try:
            logger.info(f"Processando leitura: {reading_data}")
            
            # 1. Fazer predição usando ML
            prediction_result = self.predictor.predict_from_sensor_data(reading_data)
            
            # 2. Criar objeto Reading
            reading = Reading(
                timestamp=datetime.now(),
                ph=reading_data.get('ph', 0.0),
                turbidity=reading_data.get('turbidity', 0.0),
                chloramines=reading_data.get('chloramines', 0.0),
                potability=1 if prediction_result['is_potable'] else 0
            )
            
            # 3. Salvar no banco de dados
            success = self.repository.save_reading(reading)
            
            # 4. Preparar resposta
            result = {
                'success': success,
                'timestamp': reading.timestamp.isoformat(),
                'prediction': prediction_result,
                'reading_saved': success,
                'persisted': success,  # Manter compatibilidade
                'message': 'Leitura processada com sucesso' if success else 'Erro ao salvar leitura'
            }
            
            logger.info(f"Leitura processada: {prediction_result['potability_label']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar leitura: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar leitura'
            }
    
    def get_readings(self, limit: int = 100) -> List[Dict]:
        """Recupera leituras recentes do banco de dados."""
        try:
            readings = self.repository.get_readings(limit)
            
            # Converter para dicionários
            result = []
            for reading in readings:
                result.append({
                    'id': reading.id,
                    'timestamp': reading.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f') if reading.timestamp else None,
                    'ph': reading.ph,
                    'turbidity': reading.turbidity,
                    'chloramines': reading.chloramines,
                    'potability': reading.potability,
                    'potability_label': 'POTAVEL' if reading.potability == 1 else 'NAO_POTAVEL'
                })
            
            logger.info(f"Recuperadas {len(result)} leituras")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao recuperar leituras: {e}")
            return []
    
    def get_alerts(self) -> List[Dict]:
        """Recupera alertas de água não potável."""
        try:
            alerts = self.repository.get_alerts()
            
            result = []
            for alert in alerts:
                result.append({
                    'id': alert.id,
                    'timestamp': alert.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f') if alert.timestamp else None,
                    'ph': alert.ph,
                    'turbidity': alert.turbidity,
                    'chloramines': alert.chloramines,
                    'severity': self._determine_alert_severity(alert),
                    'message': self._generate_alert_message(alert)
                })
            
            logger.info(f"Recuperados {len(result)} alertas")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao recuperar alertas: {e}")
            return []
    
    def evaluate_water_quality_detailed(self, reading_data: Dict[str, float]) -> Dict[str, any]:
        """Avaliação detalhada da qualidade da água."""
        try:
            evaluation = self.predictor.evaluate_water_quality(reading_data)
            logger.info(f"Avaliação detalhada: risco {evaluation['risk_level']}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Erro na avaliação detalhada: {e}")
            return {
                'error': str(e),
                'message': 'Erro na avaliação'
            }
    
    def get_statistics(self) -> Dict[str, any]:
        """Retorna estatísticas gerais do sistema."""
        try:
            # Recuperar leituras recentes
            recent_readings = self.get_readings(1000)  # Últimas 1000 leituras
            
            if not recent_readings:
                return {
                    'total_readings': 0,
                    'potable_percentage': 0,
                    'alerts_count': 0
                }
            
            # Calcular estatísticas
            total = len(recent_readings)
            potable_count = sum(1 for r in recent_readings if r['potability'] == 1)
            alerts = self.get_alerts()
            
            # Estatísticas de parâmetros
            ph_values = [r['ph'] for r in recent_readings if r['ph'] is not None]
            turbidity_values = [r['turbidity'] for r in recent_readings if r['turbidity'] is not None]
            
            stats = {
                'total_readings': total,
                'potable_count': potable_count,
                'non_potable_count': total - potable_count,
                'potable_percentage': (potable_count / total * 100) if total > 0 else 0,
                'alerts_count': len(alerts),
                'parameter_stats': {
                    'ph': {
                        'mean': sum(ph_values) / len(ph_values) if ph_values else 0,
                        'min': min(ph_values) if ph_values else 0,
                        'max': max(ph_values) if ph_values else 0
                    },
                    'turbidity': {
                        'mean': sum(turbidity_values) / len(turbidity_values) if turbidity_values else 0,
                        'min': min(turbidity_values) if turbidity_values else 0,
                        'max': max(turbidity_values) if turbidity_values else 0
                    }
                },
                'last_reading': recent_readings[0] if recent_readings else None
            }
            
            logger.info(f"Estatísticas calculadas: {total} leituras, {potable_count} potáveis")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {
                'error': str(e),
                'message': 'Erro ao calcular estatísticas'
            }
    
    def _determine_alert_severity(self, reading: Reading) -> str:
        """Determina a severidade do alerta baseado nos parâmetros."""
        critical_count = 0
        
        # Verificar pH crítico
        if reading.ph is not None and (reading.ph < 6.0 or reading.ph > 9.0):
            critical_count += 1
        
        # Verificar turbidez crítica
        if reading.turbidity is not None and reading.turbidity > 100:
            critical_count += 1
        
        # Verificar cloro crítico
        if reading.chloramines is not None and (reading.chloramines < 0.1 or reading.chloramines > 4.0):
            critical_count += 1
        
        if critical_count >= 2:
            return 'critica'
        elif critical_count == 1:
            return 'alta'
        else:
            return 'media'
    
    def _generate_alert_message(self, reading: Reading) -> str:
        """Gera mensagem de alerta baseada na leitura."""
        messages = []
        
        if reading.ph is not None:
            if reading.ph < 6.0:
                messages.append(f"pH muito ácido ({reading.ph:.2f})")
            elif reading.ph > 9.0:
                messages.append(f"pH muito alcalino ({reading.ph:.2f})")
        
        if reading.turbidity is not None and reading.turbidity > 25:
            messages.append(f"Turbidez elevada ({reading.turbidity:.2f} NTU)")
        
        if reading.chloramines is not None:
            if reading.chloramines < 0.1:
                messages.append(f"Cloro insuficiente ({reading.chloramines:.2f} ppm)")
            elif reading.chloramines > 4.0:
                messages.append(f"Cloro em excesso ({reading.chloramines:.2f} ppm)")
        
        if not messages:
            messages.append("Parâmetros fora dos padrões de potabilidade")
        
        return "; ".join(messages)

# Instância global para reutilização
_controller_instance = None

def get_controller() -> WaterQualityController:
    """Retorna instância singleton do controller."""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = WaterQualityController()
    return _controller_instance 