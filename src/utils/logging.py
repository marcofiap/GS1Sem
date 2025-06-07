####################################
##### Arquivo: logging.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import logging
import os
from pathlib import Path
import yaml

def setup_logging():
    """Configura o sistema de logging baseado no arquivo de configuração."""
    
    # Carregar configurações
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    log_config = config['logging']
    
    # Criar diretório de logs se não existir
    log_file = log_config['file']
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_logger(name):
    """Retorna um logger com nome específico."""
    return logging.getLogger(name) 