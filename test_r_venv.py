####################################
##### Teste R em Virtual Environment
####################################

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.r_analysis import RAnalyzer

def test_r_in_venv():
    """Teste específico para venv"""
    
    print("🔍 Testando R dentro da Virtual Environment")
    print("=" * 60)
    
    print(f"📁 Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'Não detectada')}")
    print(f"🐍 Python Executable: {sys.executable}")
    print(f"📂 Working Directory: {os.getcwd()}")
    
    print("\n🧪 Testando RAnalyzer...")
    
    try:
        analyzer = RAnalyzer()
        
        print("1. Verificando disponibilidade do R...")
        is_available = analyzer.check_r_availability()
        
        if is_available:
            print(f"✅ R disponível em: {analyzer.rscript_path}")
            
            print("\n2. Testando execução de comando R simples...")
            import subprocess
            result = subprocess.run([analyzer.rscript_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ R executou com sucesso!")
                print(f"📋 Versão: {result.stdout.strip()}")
                
                print("\n3. Testando análise simples...")
                import pandas as pd
                import numpy as np
                
                # Dados simples de teste
                test_data = pd.DataFrame({
                    'ph': np.random.normal(7, 1, 50),
                    'turbidity': np.random.normal(4, 2, 50),
                    'potability': np.random.choice([0, 1], 50)
                })
                
                result = analyzer.analyze_data(test_data)
                
                if "error" in result:
                    print(f"❌ Erro na análise: {result['error']}")
                else:
                    print("✅ Análise executada com sucesso dentro da venv!")
                    
                    if "statistics" in result:
                        stats = result["statistics"]
                        print(f"📊 Estatísticas calculadas para {len(stats)} variáveis")
                    
                    if "graphics" in result:
                        graphs = result["graphics"]
                        print(f"📈 {len(graphs)} gráficos gerados")
                    
                    return True
            else:
                print(f"❌ Erro ao executar R: {result.stderr}")
                
        else:
            print("❌ R não foi detectado dentro da venv")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_r_in_venv()
    
    if success:
        print("\n🎉 R funciona perfeitamente dentro da venv!")
        print("\n💡 Possíveis causas do problema no Streamlit:")
        print("1. Cache do Streamlit pode estar mantendo estado antigo")
        print("2. Diferenças no environment quando executado via streamlit")
        print("3. Permissões ou PATH modificado pelo Streamlit")
        
        print("\n🔧 Soluções recomendadas:")
        print("1. Limpar cache do Streamlit: streamlit cache clear")
        print("2. Reiniciar completamente o Streamlit")
        print("3. Usar caminho absoluto do R sempre")
        
    else:
        print("\n❌ Problema confirmado com venv")
        print("💡 Considere executar fora da venv ou adicionar R ao PATH") 