####################################
##### Arquivo: predict.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List
import yaml
from ..utils.logging import get_logger

logger = get_logger(__name__)

class WaterQualityPredictor:
    """Classe responsável por predições de qualidade da água."""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_path = None
        self.is_loaded = False
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações do arquivo YAML."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        self.model_path = config['ml']['model_path']
    
    def load_model(self):
        """Carrega o modelo treinado."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Modelo não encontrado em: {self.model_path}")
        
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.processor = model_data['processor']
            self.is_loaded = True
            logger.info(f"Modelo carregado com sucesso de: {self.model_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    def predict(self, features: List[float]) -> bool:
        """
        Realiza predição de potabilidade da água.
        
        Args:
            features: Lista com valores das 9 features na ordem:
                     [ph, hardness, solids, chloramines, sulfate, 
                      conductivity, organic_carbon, trihalomethanes, turbidity]
        
        Returns:
            bool: True se água é potável, False caso contrário
        """
        if not self.is_loaded:
            self.load_model()
        
        try:
            # Converter para array numpy
            X = np.array([features])
            
            # Fazer predição
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0]
            
            logger.info(f"Predição: {'Potável' if prediction == 1 else 'Não Potável'}")
            logger.info(f"Probabilidades: Não Potável={probability[0]:.3f}, Potável={probability[1]:.3f}")
            
            return bool(prediction)
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            raise
    
    def predict_from_sensor_data(self, sensor_data: Dict[str, float]) -> Dict[str, any]:
        """
        Realiza predição baseada em dados dos sensores.
        
        Args:
            sensor_data: Dicionário com dados dos sensores
                        {'ph': float, 'turbidity': float, 'chloramines': float, ...}
        
        Returns:
            Dict com resultado da predição e probabilidades
        """
        if not self.is_loaded:
            self.load_model()
        
        try:
            # Processar dados do sensor usando o processor
            features_scaled = self.processor.process_sensor_reading(sensor_data)
            
            # Fazer predição
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            result = {
                'is_potable': bool(prediction),
                'potability_label': 'POTAVEL' if prediction == 1 else 'NAO_POTAVEL',
                'confidence': float(max(probabilities)),
                'probabilities': {
                    'not_potable': float(probabilities[0]),
                    'potable': float(probabilities[1])
                },
                'sensor_data': sensor_data
            }
            
            logger.info(f"Predição de sensor: {result['potability_label']} (confiança: {result['confidence']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição de sensor: {e}")
            raise
    
    def predict_batch(self, features_list: List[List[float]]) -> List[bool]:
        """
        Realiza predições em lote.
        
        Args:
            features_list: Lista de listas com features
        
        Returns:
            Lista de predições booleanas
        """
        if not self.is_loaded:
            self.load_model()
        
        try:
            X = np.array(features_list)
            predictions = self.model.predict(X)
            
            logger.info(f"Predições em lote: {len(predictions)} amostras processadas")
            
            return [bool(pred) for pred in predictions]
            
        except Exception as e:
            logger.error(f"Erro na predição em lote: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retorna a importância das features do modelo."""
        if not self.is_loaded:
            self.load_model()
        
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.processor.feature_columns
            importance = self.model.feature_importances_
            return dict(zip(feature_names, importance))
        else:
            logger.warning("Modelo não possui atributo feature_importances_")
            return {}
    
    def evaluate_water_quality(self, sensor_data: Dict[str, float]) -> Dict[str, any]:
        """
        Avalia qualidade da água com análise detalhada.
        
        Args:
            sensor_data: Dados dos sensores
        
        Returns:
            Análise completa da qualidade da água
        """
        prediction_result = self.predict_from_sensor_data(sensor_data)
        
        # Análise de parâmetros individuais
        parameter_analysis = self._analyze_parameters(sensor_data)
        
        # Determinar nível de risco
        risk_level = self._determine_risk_level(prediction_result, parameter_analysis)
        
        result = {
            **prediction_result,
            'parameter_analysis': parameter_analysis,
            'risk_level': risk_level,
            'recommendations': self._get_recommendations(parameter_analysis, risk_level)
        }
        
        return result
    
    def _analyze_parameters(self, sensor_data: Dict[str, float]) -> Dict[str, Dict]:
        """Analisa parâmetros individuais da água."""
        analysis = {}
        
        # Análise do pH
        ph = sensor_data.get('ph', 7.0)
        if 6.5 <= ph <= 8.5:
            ph_status = 'normal'
        elif 6.0 <= ph < 6.5 or 8.5 < ph <= 9.0:
            ph_status = 'atencao'
        else:
            ph_status = 'critico'
        
        analysis['ph'] = {
            'value': ph,
            'status': ph_status,
            'ideal_range': '6.5 - 8.5'
        }
        
        # Análise da turbidez
        turbidity = sensor_data.get('turbidity', 4.0)
        if turbidity < 5:
            turbidity_status = 'normal'
        elif turbidity < 25:
            turbidity_status = 'atencao'
        else:
            turbidity_status = 'critico'
        
        analysis['turbidity'] = {
            'value': turbidity,
            'status': turbidity_status,
            'ideal_range': '< 5 NTU'
        }
        
        # Análise do cloro
        chloramines = sensor_data.get('chloramines', 0.0)
        if 0.2 <= chloramines <= 2.0:
            chlor_status = 'normal'
        elif 0.1 <= chloramines < 0.2 or 2.0 < chloramines <= 4.0:
            chlor_status = 'atencao'
        else:
            chlor_status = 'critico'
        
        analysis['chloramines'] = {
            'value': chloramines,
            'status': chlor_status,
            'ideal_range': '0.2 - 2.0 ppm'
        }
        
        return analysis
    
    def _determine_risk_level(self, prediction_result: Dict, parameter_analysis: Dict) -> str:
        """Determina nível de risco baseado na predição e análise de parâmetros."""
        if not prediction_result['is_potable']:
            return 'alto'
        
        critical_params = sum(1 for param in parameter_analysis.values() if param['status'] == 'critico')
        attention_params = sum(1 for param in parameter_analysis.values() if param['status'] == 'atencao')
        
        if critical_params > 0:
            return 'alto'
        elif attention_params >= 2:
            return 'medio'
        elif attention_params == 1:
            return 'baixo'
        else:
            return 'muito_baixo'
    
    def _get_recommendations(self, parameter_analysis: Dict, risk_level: str) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        if risk_level == 'alto':
            recommendations.append("⚠️ ÁGUA NÃO RECOMENDADA PARA CONSUMO")
            recommendations.append("Procure fonte alternativa de água potável")
        
        for param, analysis in parameter_analysis.items():
            if analysis['status'] == 'critico':
                if param == 'ph':
                    recommendations.append(f"pH crítico ({analysis['value']:.2f}) - considere tratamento")
                elif param == 'turbidity':
                    recommendations.append(f"Turbidez alta ({analysis['value']:.2f} NTU) - filtração necessária")
                elif param == 'chloramines':
                    recommendations.append(f"Nível de cloro inadequado ({analysis['value']:.2f} ppm)")
        
        if risk_level in ['muito_baixo', 'baixo']:
            recommendations.append("✅ Água dentro dos padrões de qualidade")
        
        return recommendations

# Instância global para reutilização
_predictor_instance = None

def get_predictor() -> WaterQualityPredictor:
    """Retorna instância singleton do preditor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = WaterQualityPredictor()
    return _predictor_instance

def predict(features: List[float]) -> bool:
    """Função utilitária para predição simples."""
    predictor = get_predictor()
    return predictor.predict(features) 