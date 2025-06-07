#!/usr/bin/env python3
####################################
##### Teste R para Streamlit
####################################

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.r_analysis import RAnalyzer

def test_r_for_streamlit():
    """Teste específico para uso no Streamlit"""
    
    print("🔍 Teste R para Streamlit")
    print("=" * 50)
    
    print(f"📁 Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'Não detectada')}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📂 Working Dir: {os.getcwd()}")
    
    # Teste 1: Criação da instância
    print("\n1. Criando instância RAnalyzer...")
    try:
        analyzer = RAnalyzer()
        print("✅ Instância criada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar instância: {e}")
        return False
    
    # Teste 2: Verificação de disponibilidade
    print("\n2. Verificando disponibilidade do R...")
    try:
        is_available = analyzer.check_r_availability()
        if is_available:
            print(f"✅ R disponível em: {analyzer.rscript_path}")
        else:
            print("❌ R não encontrado")
            
            # Tentar diagnóstico
            print("\n🔍 Diagnóstico:")
            import glob
            r_installations = glob.glob(r'C:\Program Files\R\R-*\bin\Rscript.exe')
            if r_installations:
                print(f"📋 R encontrado em: {r_installations}")
                print("💡 Pode ser problema de permissões ou subprocess")
            else:
                print("❌ Nenhuma instalação do R encontrada")
                
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Teste 3: Teste simples de análise
    print("\n3. Teste de análise simples...")
    try:
        import pandas as pd
        import numpy as np
        
        test_data = pd.DataFrame({
            'ph': [7.1, 6.8, 7.3, 6.9, 7.0],
            'turbidity': [3.2, 4.1, 2.8, 3.7, 3.5],
            'potability': [1, 0, 1, 0, 1]
        })
        
        result = analyzer.analyze_data(test_data)
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        else:
            print("✅ Análise executada com sucesso!")
            
            if "statistics" in result:
                stats = result["statistics"]
                print(f"📊 Estatísticas: {len(stats)} variáveis")
                
            if "graphics" in result:
                graphics = result["graphics"]
                print(f"📈 Gráficos: {len(graphics)} gerados")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro no teste de análise: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_r_for_streamlit()
    
    if success:
        print("\n🎉 R está funcionando perfeitamente!")
        print("\n📋 Para usar no Streamlit:")
        print("1. Execute: python run_app.py")
        print("2. Acesse: http://localhost:8501")
        print("3. Vá para: Análise em R")
        print("4. Use o debug se necessário")
    else:
        print("\n❌ Problemas encontrados com R")
        print("\n🔧 Soluções:")
        print("1. Verifique se R está instalado")
        print("2. Execute como administrador")
        print("3. Adicione R ao PATH do sistema")
        print("4. Reinicie o terminal/VSCode") 