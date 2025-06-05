# 🌊 Guia de Configuração Wokwi - Sistema de Qualidade da Água

## 📋 Pré-requisitos

- [x] Sistema Python funcionando (virtual environment ativo)
- [x] Banco Oracle configurado e conectado
- [x] Modelo ML treinado
- [x] Conta no [Wokwi](https://wokwi.com) (gratuita)

## 🚀 Passo 1: Descobrir seu IP Local

Execute o script para descobrir automaticamente seu IP:

```bash
python descobrir_ip.py
```

**Exemplo de saída:**
```
✅ Encontrados 1 endereços IP:
1. 192.168.1.100 (via Principal)

📍 IP recomendado: 192.168.1.100
📝 Atualize o arquivo src/main.cpp:
   String serverName = "http://192.168.1.100:8000/data";
```

## 🔧 Passo 2: Configurar o ESP32

1. **Abra o arquivo `src/main.cpp`**
2. **Encontre a linha:**
   ```cpp
   String serverName = "http://192.168.1.100:8000/data";
   ```
3. **Substitua pelo IP descoberto:**
   ```cpp
   String serverName = "http://SEU_IP_AQUI:8000/data";
   ```

## 🖥️ Passo 3: Iniciar o Servidor

Execute o servidor Flask integrado:

```bash
python servidor_wokwi.py
```

**Você deve ver:**
```
🌊 SERVIDOR WOKWI - QUALIDADE DA ÁGUA
============================================================
✅ Módulos do sistema ML importados com sucesso
✅ Sistema de ML conectado e pronto
🚀 Iniciando servidor Flask...
🔗 Endpoints ESP32: http://0.0.0.0:8000/data
📊 Status: http://0.0.0.0:8000/status
```

## 🌐 Passo 4: Configurar o Wokwi

1. **Acesse [wokwi.com](https://wokwi.com)**
2. **Crie um novo projeto ESP32**
3. **Cole o código do `src/main.cpp`**
4. **Adicione os componentes:**
   - ESP32 DevKit v1
   - Display OLED SSD1306 (128x64)
   - 3 LEDs (Verde, Amarelo, Vermelho)
   - 1 Botão (pushbutton)
   - 4 Potenciômetros (simulando sensores)

## 🔌 Passo 5: Conexões no Wokwi

### Sensores (Potenciômetros):
- **pH**: Pino 35
- **Turbidez**: Pino 32  
- **Cloro**: Pino 34
- **Condutividade**: Pino 33

### LEDs:
- **Verde (Potável)**: Pino 4
- **Amarelo (Suspeita)**: Pino 16
- **Vermelho (Não Potável)**: Pino 17

### Botão:
- **Enviar Dados**: Pino 5

### Display OLED:
- **SDA**: Pino 21
- **SCL**: Pino 22
- **VCC**: 3.3V
- **GND**: GND

## ▶️ Passo 6: Testar o Sistema

1. **Inicie a simulação no Wokwi**
2. **Ajuste os potenciômetros** (simular diferentes valores de sensores)
3. **Pressione o botão** para enviar dados
4. **Observe:**
   - Display mostra valores dos sensores
   - LED acende conforme predição
   - Terminal do servidor mostra logs

## 📊 Passo 7: Monitorar Resultados

### No Terminal do Servidor:
```
[14:30:15] Dados recebidos do ESP32 - pH:7.2, Turbidez:3.5, Cloro:1.8, Condutividade:450.0
✅ Predição: POTAVEL (Confiança: 72.5%, Risco: LOW)
💾 Dados salvos no banco Oracle
```

### No Dashboard (http://localhost:8501):
- Vá para a página "Dashboard"
- Veja os dados em tempo real
- Analise gráficos e estatísticas

## 🔍 Endpoints Disponíveis

| Endpoint | Descrição | Exemplo |
|----------|-----------|---------|
| `/data` | Recebe dados do ESP32 | `GET /data?ph=7.2&turbidity=3.5&chlorine=1.8&conductivity=450` |
| `/status` | Status do sistema | `GET /status` |
| `/historico` | Histórico de leituras | `GET /historico?limit=50` |
| `/alertas` | Alertas do sistema | `GET /alertas?limit=20` |
| `/test` | Teste de funcionamento | `GET /test` |

## 🛠️ Solução de Problemas

### ❌ "Falha de comunicação" no ESP32
**Possíveis causas:**
- IP incorreto no código ESP32
- Servidor Flask não está rodando
- Firewall bloqueando porta 8000
- VPN interferindo na conexão

**Soluções:**
1. Verifique o IP com `python descobrir_ip.py`
2. Teste o servidor: `curl http://SEU_IP:8000/test`
3. Desative temporariamente o firewall
4. Desative a VPN

### ❌ "ERRO_ML" no servidor
**Possíveis causas:**
- Modelo ML não carregado
- Banco Oracle desconectado
- Dados de entrada inválidos

**Soluções:**
1. Execute `python train_model.py` novamente
2. Verifique conexão Oracle
3. Teste com dados válidos

### ❌ Wokwi não conecta
**Possíveis causas:**
- ESP32 não consegue acessar a rede local
- Configuração de rede do navegador

**Soluções:**
1. Use WiFi real em vez de simulação
2. Configure proxy se necessário
3. Teste em navegador diferente

## 📈 Cenários de Teste

### Água Potável:
- pH: 7.0-7.5
- Turbidez: 1-3 NTU
- Cloro: 1.0-2.0 mg/L
- Condutividade: 200-500 µS/cm

### Água Suspeita:
- pH: 6.0-6.5 ou 8.5-9.0
- Turbidez: 5-10 NTU
- Cloro: 0.5-1.0 ou 2.5-3.0 mg/L
- Condutividade: 100-200 ou 800-1000 µS/cm

### Água Não Potável:
- pH: < 6.0 ou > 9.0
- Turbidez: > 15 NTU
- Cloro: < 0.2 ou > 4.0 mg/L
- Condutividade: < 50 ou > 1500 µS/cm

## 🎯 Dicas de Uso

1. **Mantenha o servidor rodando** enquanto usa o Wokwi
2. **Monitore os logs** para debug
3. **Use o dashboard** para análise detalhada
4. **Teste diferentes cenários** de qualidade da água
5. **Verifique alertas** no sistema

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do servidor
2. Teste cada endpoint individualmente
3. Use `python descobrir_ip.py` novamente
4. Reinicie o servidor e a simulação 