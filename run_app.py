#!/usr/bin/env python3
####################################
##### Arquivo: run_app.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

"""
Script principal para executar a aplicação Streamlit
do Sistema de Monitoramento de Qualidade da Água.

Uso:
    python run_app.py
"""

import os
import sys
import subprocess
from pathlib import Path

import yaml


def main():
    print("="*60)
    print("SISTEMA DE MONITORAMENTO DE QUALIDADE DA ÁGUA")
    print("Iniciando Interface Web (Streamlit)")
    print("="*60)
    
    # Verificar se o modelo existe
    try:
        project_root = Path(__file__).parent

        config_path = project_root / "config" / "config.yaml"


        if not config_path.exists():
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            sys.exit(1)

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        if 'ml' not in config or 'model_path' not in config['ml']:
            print("❌ Configuração inválida: 'ml.model_path' não encontrado no arquivo config.yaml")
            sys.exit(1)

        model_path = Path(config['ml']['model_path'])

    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {str(e)}")
        sys.exit(1)

    if not model_path.exists():
        print("⚠️  ATENÇÃO: Modelo não encontrado!")
        print("Execute primeiro: python train_model.py")
        print("Continuando mesmo assim...")
    
    # Caminho para a aplicação
    app_path = Path("src/ui/app.py")
    
    if not app_path.exists():
        print(f"❌ Arquivo da aplicação não encontrado: {app_path}")
        sys.exit(1)
    
    print(f"📁 Executando aplicação: {app_path}")
    print("🌐 A aplicação será aberta no navegador automaticamente")
    print("📍 URL: http://localhost:8501")
    print("\n💡 Para parar a aplicação, pressione Ctrl+C")
    print("="*60)
    
    try:
        # Executar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Aplicação interrompida pelo usuário")
        print("Obrigado por usar o Sistema de Monitoramento!")

if __name__ == "__main__":
    main() 