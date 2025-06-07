####################################
##### Arquivo: test_r_analysis.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.r_analysis import RAnalyzer

def test_r_analysis():
    """Testa o módulo de análise R."""
    
    print("🧪 Testando Módulo de Análise R")
    print("=" * 50)
    
    # Verificar se R está disponível
    r_analyzer = RAnalyzer()
    
    print("1. Verificando disponibilidade do R...")
    r_available = r_analyzer.check_r_availability()
    
    if not r_available:
        print("❌ R não está disponível no sistema!")
        print("\nInstale o R em: https://cran.r-project.org/")
        return False
    
    print("✅ R está disponível!")
    
    # Tentar instalar pacotes necessários
    print("\n2. Verificando/instalando pacotes R...")
    try:
        packages_ok = r_analyzer.install_required_packages()
        if packages_ok:
            print("✅ Pacotes R instalados com sucesso!")
        else:
            print("⚠️ Alguns pacotes podem não ter sido instalados corretamente")
    except Exception as e:
        print(f"❌ Erro ao instalar pacotes: {e}")
    
    # Criar dados de teste
    print("\n3. Criando dados de teste...")
    np.random.seed(42)
    test_data = pd.DataFrame({
        'ph': np.random.normal(7.0, 1.5, 100),
        'hardness': np.random.normal(200, 50, 100),
        'solids': np.random.normal(20000, 5000, 100),
        'chloramines': np.random.normal(7.0, 2.0, 100),
        'sulfate': np.random.normal(300, 100, 100),
        'conductivity': np.random.normal(400, 150, 100),
        'organic_carbon': np.random.normal(14, 5, 100),
        'trihalomethanes': np.random.normal(80, 30, 100),
        'turbidity': np.random.normal(4, 2, 100),
        'potability': np.random.choice([0, 1], 100, p=[0.6, 0.4])
    })
    
    print(f"✅ Dados criados: {len(test_data)} registros, {len(test_data.columns)} variáveis")
    
    # Executar análise
    print("\n4. Executando análise R...")
    try:
        results = r_analyzer.analyze_data(test_data)
        
        if "error" in results:
            print(f"❌ Erro na análise: {results['error']}")
            return False
        
        print("✅ Análise executada com sucesso!")
        
        # Verificar resultados
        print("\n5. Verificando resultados...")
        
        if "statistics" in results:
            stats = results["statistics"]
            print(f"   - Estatísticas para {len(stats)} variáveis")
            
            for var, data in stats.items():
                print(f"   - {var}:")
                if "tendencia_central" in data:
                    tc = data["tendencia_central"]
                    print(f"     Média: {tc.get('media', 'N/A'):.3f}")
                    print(f"     Mediana: {tc.get('mediana', 'N/A'):.3f}")
        
        if "graphics" in results:
            graphics = results["graphics"]
            print(f"   - {len(graphics)} gráficos gerados")
            
            for graph_name in graphics.keys():
                print(f"     - {graph_name}")
        
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def test_with_real_data():
    """Testa com dados reais do dataset."""
    
    print("\n🌊 Testando com Dataset Real")
    print("=" * 50)
    
    # Verificar se dataset existe
    dataset_path = Path("water_potability.csv")
    
    if not dataset_path.exists():
        print("❌ Dataset water_potability.csv não encontrado!")
        print("   Coloque o arquivo na raiz do projeto")
        return False
    
    print("✅ Dataset encontrado!")
    
    # Carregar dados
    df = pd.read_csv(dataset_path)
    print(f"📊 Dataset carregado: {len(df)} registros")
    
    # Limitar para análise mais rápida
    sample_df = df.head(200)
    print(f"📋 Usando amostra de {len(sample_df)} registros")
    
    # Executar análise
    r_analyzer = RAnalyzer()
    
    try:
        results = r_analyzer.analyze_data(sample_df)
        
        if "error" in results:
            print(f"❌ Erro na análise: {results['error']}")
            return False
        
        print("✅ Análise do dataset real concluída!")
        
        # Mostrar algumas estatísticas
        if "statistics" in results:
            stats = results["statistics"]
            print(f"\n📈 Resumo das análises para {len(stats)} variáveis:")
            
            for var, data in list(stats.items())[:3]:  # Mostrar apenas 3
                if "tendencia_central" in data:
                    tc = data["tendencia_central"]
                    disp = data.get("dispersao", {})
                    print(f"\n   {var.upper()}:")
                    print(f"   Média: {tc.get('media', 'N/A'):.3f}")
                    print(f"   Desvio Padrão: {disp.get('desvio_padrao', 'N/A'):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise do dataset: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando Testes do Módulo R")
    print("=" * 60)
    
    # Teste básico
    basic_test = test_r_analysis()
    
    if basic_test:
        # Teste com dados reais
        real_test = test_with_real_data()
        
        if real_test:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("\n📋 Próximos passos:")
            print("1. Execute o servidor: python -m src.api.servidor")
            print("2. Execute o Streamlit: python run_app.py")
            print("3. Acesse a página 'Análise em R' na interface")
        else:
            print("\n⚠️ Teste básico passou, mas teste com dados reais falhou")
    else:
        print("\n❌ Teste básico falhou - verifique a instalação do R")
    
    print("\n" + "=" * 60) 