#!/bin/bash

echo "===================================="
echo "  Compilando projeto ESP32 "
echo "  Sistema de Monitoramento de Água"
echo "===================================="
echo

# Verifica se o PlatformIO está instalado
if ! command -v pio &> /dev/null; then
    echo "[ERRO] PlatformIO CLI não encontrado!"
    echo
    echo "Para instalar o PlatformIO:"
    echo "1. Instale o Python: https://python.org/downloads/"
    echo "2. Execute: pip install platformio"
    echo "3. Reinicie o terminal"
    echo
    exit 1
fi

echo "[INFO] PlatformIO encontrado! Iniciando compilação..."
echo

# Compila o projeto
echo "[INFO] Compilando firmware ESP32..."
pio run

if [ $? -eq 0 ]; then
    echo
    echo "===================================="
    echo "  COMPILAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "===================================="
    echo
    echo "O arquivo firmware.bin foi gerado em:"
    echo ".pio/build/esp32dev/firmware.bin"
    echo
    echo "Agora você pode:"
    echo "1. Abrir o Wokwi no navegador"
    echo "2. Carregar o diagram.json"
    echo "3. Clicar em 'Start the Simulation'"
    echo
else
    echo
    echo "===================================="
    echo "  ERRO NA COMPILAÇÃO!"
    echo "===================================="
    echo
    echo "Verifique:"
    echo "1. Se todas as dependências estão instaladas"
    echo "2. Se o código não tem erros de sintaxe"
    echo "3. Se o platformio.ini está correto"
    echo
fi 