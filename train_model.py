#!/usr/bin/env python3
####################################
##### Arquivo: train_model.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

"""
Script principal para treinar o modelo de Machine Learning
para classificação de qualidade da água.

Uso:
    python train_model.py
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.model.train import main

if __name__ == "__main__":
    print("="*60)
    print("SISTEMA DE MONITORAMENTO DE QUALIDADE DA ÁGUA")
    print("Treinamento do Modelo de Machine Learning")
    print("="*60)
    
    try:
        main()
        print("\n" + "="*60)
        print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("O modelo foi salvo e está pronto para uso.")
        print("="*60)
    except Exception as e:
        print(f"\n❌ ERRO NO TREINAMENTO: {e}")
        print("Verifique os logs para mais detalhes.")
        sys.exit(1) 