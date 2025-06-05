#!/usr/bin/env python3
####################################
##### Arquivo: descobrir_ip.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

"""
Script para descobrir o IP local da máquina para configurar o ESP32/Wokwi.
"""

import socket
import subprocess
import platform
import sys

def descobrir_ip_local():
    """
    Descobre o IP local da máquina usando diferentes métodos.
    """
    ips = []
    
    # Método 1: Conectar a um servidor externo
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_principal = s.getsockname()[0]
            ips.append(("Principal", ip_principal))
    except:
        pass
    
    # Método 2: Hostname
    try:
        hostname = socket.gethostname()
        ip_hostname = socket.gethostbyname(hostname)
        if ip_hostname != "127.0.0.1":
            ips.append(("Hostname", ip_hostname))
    except:
        pass
    
    # Método 3: Interface de rede (específico do sistema)
    sistema = platform.system().lower()
    
    if sistema == "darwin":  # macOS
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line and 'inet 169.254' not in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if part == 'inet' and i + 1 < len(parts):
                            ip = parts[i + 1]
                            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                                ips.append(("Interface", ip))
        except:
            pass
    
    elif sistema == "linux":
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            ip_list = result.stdout.strip().split()
            for ip in ip_list:
                if not ip.startswith('127.') and (ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.')):
                    ips.append(("Linux", ip))
        except:
            pass
    
    elif sistema == "windows":
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4' in line:
                    ip = line.split(':')[-1].strip()
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        ips.append(("Windows", ip))
        except:
            pass
    
    return ips

def main():
    print("="*60)
    print("🔍 DESCOBRINDO IP LOCAL PARA WOKWI")
    print("="*60)
    
    # Descobrir IPs
    ips = descobrir_ip_local()
    
    if not ips:
        print("❌ Não foi possível descobrir o IP local automaticamente.")
        print("\n💡 Tente descobrir manualmente:")
        print("   • Windows: digite 'ipconfig' no prompt")
        print("   • Mac: digite 'ifconfig' no terminal")
        print("   • Linux: digite 'hostname -I' no terminal")
        return
    
    print(f"✅ Encontrados {len(ips)} endereços IP:")
    print()
    
    # Listar IPs encontrados
    for i, (metodo, ip) in enumerate(ips, 1):
        print(f"{i}. {ip} (via {metodo})")
    
    print()
    print("="*60)
    print("🔧 CONFIGURAÇÃO DO ESP32/WOKWI")
    print("="*60)
    
    # IP recomendado (primeiro da lista)
    ip_recomendado = ips[0][1]
    
    print(f"📍 IP recomendado: {ip_recomendado}")
    print()
    print("📝 Atualize o arquivo src/main.cpp:")
    print(f'   String serverName = "http://{ip_recomendado}:8000/data";')
    print()
    print("🚀 Passos para usar:")
    print("1. Execute o servidor: python servidor_wokwi.py")
    print("2. Abra o Wokwi no navegador")
    print("3. Carregue o projeto ESP32")
    print("4. Pressione o botão no simulador para enviar dados")
    print()
    print("🌐 URLs importantes:")
    print(f"   • Servidor Wokwi: http://{ip_recomendado}:8000/")
    print(f"   • Status: http://{ip_recomendado}:8000/status")
    print(f"   • Dashboard: http://localhost:8501")
    print()
    
    # Verificar se há diferentes IPs
    if len(ips) > 1:
        unique_ips = list(set([ip for _, ip in ips]))
        if len(unique_ips) > 1:
            print("⚠️  ATENÇÃO: Múltiplos IPs encontrados!")
            print("   Se um não funcionar, tente os outros:")
            for _, ip in ips[1:]:
                print(f"   • http://{ip}:8000/data")
            print()
    
    print("💡 Dicas:")
    print("   • Certifique-se de que o firewall permite conexões na porta 8000")
    print("   • Se estiver usando VPN, pode ser necessário desativá-la")
    print("   • O Wokwi precisa acessar sua máquina na rede local")
    print("="*60)

if __name__ == "__main__":
    main() 