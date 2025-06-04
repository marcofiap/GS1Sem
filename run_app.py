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

def main():
    print("="*60)
    print("SISTEMA DE MONITORAMENTO DE QUALIDADE DA ÁGUA")
    print("Iniciando Interface Web (Streamlit)")
    print("="*60)
    
    # Verificar se o modelo existe
    model_path = Path("src/model/water_quality_model.pkl")
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