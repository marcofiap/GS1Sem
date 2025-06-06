####################################
##### Arquivo: __init__.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

from .predict import WaterQualityPredictor, get_predictor, predict
from .train import WaterQualityModelTrainer

__all__ = ['WaterQualityPredictor', 'get_predictor', 'predict', 'WaterQualityModelTrainer'] 