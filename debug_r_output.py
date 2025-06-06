#!/usr/bin/env python3
####################################
##### Debug R Output
####################################

import sys
import os
import json
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.r_analysis import RAnalyzer
import pandas as pd
import numpy as np

def debug_r_output():
    """Debug dos resultados do R"""
    
    print("🔍 Debug dos Resultados do R")
    print("=" * 60)
    
    # Criar dados de teste simples
    test_data = pd.DataFrame({
        'ph': [7.1, 6.8, 7.3, 6.9, 7.0, 7.2, 6.7, 7.4],
        'turbidity': [3.2, 4.1, 2.8, 3.7, 3.5, 3.0, 4.0, 2.9],
        'potability': [1, 0, 1, 0, 1, 1, 0, 1]
    })
    
    print(f"📊 Dados de teste: {len(test_data)} registros")
    
    analyzer = RAnalyzer()
    
    # Verificar se R está disponível
    if not analyzer.check_r_availability():
        print("❌ R não disponível")
        return
    
    print(f"✅ R encontrado: {analyzer.rscript_path}")
    
    # Executar análise
    print("\n🧪 Executando análise...")
    results = analyzer.analyze_data(test_data)
    
    if "error" in results:
        print(f"❌ Erro: {results['error']}")
        return
    
    print("✅ Análise executada!")
    
    # Debug detalhado dos resultados
    print("\n📋 Estrutura dos Resultados:")
    print("=" * 40)
    
    for key, value in results.items():
        print(f"\n🔑 {key}: {type(value)}")
        
        if key == "statistics":
            print("📊 Estatísticas:")
            for var, stats in value.items():
                print(f"  📈 {var}: {type(stats)}")
                
                for stat_type, stat_data in stats.items():
                    print(f"    🔹 {stat_type}: {type(stat_data)}")
                    
                    if stat_type == "separatrizes" and "quartis" in stat_data:
                        print(f"      📊 quartis: {type(stat_data['quartis'])}")
                        print(f"      📊 quartis content: {stat_data['quartis']}")
                        
                        # Testar acesso individual
                        quartis = stat_data['quartis']
                        print(f"      🔍 Testando acessos:")
                        
                        if isinstance(quartis, dict):
                            for key in quartis.keys():
                                print(f"        ✅ quartis['{key}'] = {quartis[key]}")
                        elif isinstance(quartis, list):
                            print(f"        📋 quartis é lista: {quartis}")
                        else:
                            print(f"        ⚠️ quartis é {type(quartis)}: {quartis}")
        
        elif key == "graphics":
            print(f"📈 Gráficos: {len(value)} encontrados")
            for graph_name in value.keys():
                print(f"  🖼️ {graph_name}")
    
    # Simular o que está acontecendo no app.py
    print("\n🧪 Simulando acesso como no app.py:")
    print("=" * 40)
    
    try:
        if "statistics" in results:
            stats = results["statistics"]
            for var, data in stats.items():
                print(f"\n📈 Processando {var}...")
                
                if "separatrizes" in data:
                    sep = data["separatrizes"]
                    print(f"  📊 separatrizes: {type(sep)}")
                    
                    if "quartis" in sep:
                        quartis = sep["quartis"]
                        print(f"  📊 quartis: {type(quartis)}")
                        print(f"  📊 quartis content: {quartis}")
                        
                        # Tentar acessar como fazemos no app.py
                        try:
                            q1 = quartis.get('25%', 0)
                            print(f"  ✅ Q1 via get(): {q1}")
                        except AttributeError as e:
                            print(f"  ❌ Erro no get(): {e}")
                            
                            # Se for lista, tentar acesso por índice
                            if isinstance(quartis, list) and len(quartis) >= 3:
                                print(f"  💡 Tentando acesso por lista:")
                                print(f"    Q1 (índice 0): {quartis[0]}")
                                print(f"    Q2 (índice 1): {quartis[1]}")
                                print(f"    Q3 (índice 2): {quartis[2]}")
    
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_r_output() 