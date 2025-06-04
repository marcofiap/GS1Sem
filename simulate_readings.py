#!/usr/bin/env python3
####################################
##### Arquivo: simulate_readings.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

"""
Script para simular leituras de sensores e popular o banco Oracle.
Usado para demonstração quando não há dados reais do ESP32.
"""

import sys
import os
import random
import time
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.controller import get_controller
from src.utils.logging import setup_logging, get_logger

# Configurar logging
setup_logging()
logger = get_logger(__name__)

def generate_realistic_reading():
    """Gera uma leitura realística de sensor."""
    
    # Cenários diferentes de qualidade da água
    scenarios = [
        # Água potável
        {
            'ph': random.uniform(6.5, 8.5),
            'turbidity': random.uniform(0.5, 4.0),
            'chloramines': random.uniform(0.2, 2.0),
            'weight': 0.4  # 40% das leituras
        },
        # Água com problemas leves
        {
            'ph': random.uniform(6.0, 6.5) if random.random() < 0.5 else random.uniform(8.5, 9.0),
            'turbidity': random.uniform(4.0, 15.0),
            'chloramines': random.uniform(0.1, 0.2) if random.random() < 0.5 else random.uniform(2.0, 3.0),
            'weight': 0.35  # 35% das leituras
        },
        # Água com problemas graves
        {
            'ph': random.uniform(5.0, 6.0) if random.random() < 0.5 else random.uniform(9.0, 10.0),
            'turbidity': random.uniform(15.0, 50.0),
            'chloramines': random.uniform(0.0, 0.1) if random.random() < 0.5 else random.uniform(3.0, 5.0),
            'weight': 0.25  # 25% das leituras
        }
    ]
    
    # Escolher cenário baseado nos pesos
    scenario = random.choices(scenarios, weights=[s['weight'] for s in scenarios])[0]
    
    # Adicionar pequena variação
    reading = {
        'ph': round(scenario['ph'] + random.uniform(-0.2, 0.2), 2),
        'turbidity': round(max(0.1, scenario['turbidity'] + random.uniform(-1.0, 1.0)), 2),
        'chloramines': round(max(0.0, scenario['chloramines'] + random.uniform(-0.1, 0.1)), 2)
    }
    
    return reading

def simulate_readings_batch(controller, num_readings=50, time_range_hours=24):
    """Simula um lote de leituras distribuídas no tempo."""
    
    print(f"🔄 Simulando {num_readings} leituras distribuídas em {time_range_hours} horas...")
    
    # Calcular intervalos de tempo
    start_time = datetime.now() - timedelta(hours=time_range_hours)
    time_interval = timedelta(hours=time_range_hours) / num_readings
    
    successful_readings = 0
    failed_readings = 0
    
    for i in range(num_readings):
        try:
            # Gerar leitura
            reading_data = generate_realistic_reading()
            
            # Simular timestamp realista
            reading_time = start_time + (time_interval * i)
            
            # Processar através do controller (inclui ML e persistência)
            result = controller.ingest_reading(reading_data)
            
            if result['success']:
                successful_readings += 1
                prediction = result['prediction']['potability_label']
                print(f"✅ Leitura {i+1}/{num_readings}: pH={reading_data['ph']}, "
                      f"Turbidez={reading_data['turbidity']}, "
                      f"Cloro={reading_data['chloramines']} → {prediction}")
            else:
                failed_readings += 1
                print(f"❌ Leitura {i+1}/{num_readings}: Falha - {result.get('message', 'Erro desconhecido')}")
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)
            
        except Exception as e:
            failed_readings += 1
            print(f"❌ Erro na leitura {i+1}: {e}")
    
    print(f"\n📊 Resumo da Simulação:")
    print(f"✅ Sucessos: {successful_readings}")
    print(f"❌ Falhas: {failed_readings}")
    print(f"📈 Taxa de sucesso: {successful_readings/num_readings*100:.1f}%")

def simulate_real_time_readings(controller, num_readings=10, interval_seconds=5):
    """Simula leituras em tempo real."""
    
    print(f"🔄 Simulando {num_readings} leituras em tempo real (intervalo: {interval_seconds}s)")
    print("💡 Pressione Ctrl+C para parar\n")
    
    try:
        for i in range(num_readings):
            reading_data = generate_realistic_reading()
            
            try:
                result = controller.ingest_reading(reading_data)
                
                if result['success']:
                    prediction = result['prediction']['potability_label']
                    confidence = result['prediction']['confidence']
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    status_emoji = "✅" if prediction == "POTAVEL" else "⚠️"
                    print(f"{status_emoji} [{timestamp}] pH={reading_data['ph']}, "
                          f"Turbidez={reading_data['turbidity']}, "
                          f"Cloro={reading_data['chloramines']} → {prediction} ({confidence:.1%})")
                else:
                    print(f"❌ [{timestamp}] Falha: {result.get('message', 'Erro')}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar leitura: {e}")
            
            if i < num_readings - 1:  # Não aguardar após a última leitura
                time.sleep(interval_seconds)
                
    except KeyboardInterrupt:
        print("\n👋 Simulação interrompida pelo usuário")

def main():
    """Função principal."""
    print("="*60)
    print("SIMULADOR DE LEITURAS DE QUALIDADE DA ÁGUA")
    print("="*60)
    
    try:
        controller = get_controller()
        
        print("Escolha o modo de simulação:")
        print("1. Lote de leituras históricas (rápido)")
        print("2. Leituras em tempo real (lento)")
        print("3. Lote pequeno para teste (10 leituras)")
        
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == "1":
            num_readings = int(input("Número de leituras (padrão 50): ") or "50")
            time_range = int(input("Distribuir em quantas horas (padrão 24): ") or "24")
            simulate_readings_batch(controller, num_readings, time_range)
            
        elif choice == "2":
            num_readings = int(input("Número de leituras (padrão 10): ") or "10")
            interval = int(input("Intervalo em segundos (padrão 5): ") or "5")
            simulate_real_time_readings(controller, num_readings, interval)
            
        elif choice == "3":
            print("Executando teste rápido com 10 leituras...")
            simulate_readings_batch(controller, 10, 2)
            
        else:
            print("❌ Opção inválida!")
            return
        
        print("\n🎉 Simulação concluída!")
        print("🌐 Acesse o dashboard em http://localhost:8501 para ver os dados")
        
    except Exception as e:
        print(f"❌ Erro durante simulação: {e}")
        logger.error(f"Erro na simulação: {e}")

if __name__ == "__main__":
    main() 