# 🎮 Simulador ESP32 - Sistema de Monitoramento de Água

## 🚀 Esta instalação resolve problemas de incompatibilidade no windows

```bash
# 1. Instalar todas as dependências
cd simularsensor
pip install -r requirements.txt

# 2. Compilar (Windows) - (se ocorrer erro ao clicar play no wokwi, execute o comando abaixo)
compile.bat

# 2. Compilar (Linux/Mac) - (se ocorrer erro ao clicar play no wokwi, execute o comando abaixo)
./compile.sh

# 3. Abrir o arquivo diagram.json
# 4. Clicar em "Start the Simulation"

# 5. Depois de dar play no diagram com wokwi, é necessário rodar o servidor da raiz do projeto para receber dados dos sensores emulados 
python src/api/servidor.py 