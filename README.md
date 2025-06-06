# FIAP - Faculdade de Informática e Administração Paulista 

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="imagem/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Sistema de Monitoramento de Qualidade da Água 💧

## Grupo 52

## 👨‍🎓 Integrantes: 
- <a href="https://github.com/FelipeSabinoTMRS">Felipe Sabino da Silva</a>
- <a href="https://github.com/juanvoltolini-rm562890">Juan Felipe Voltolini</a>
- <a href="https://github.com/Luiz-FIAP">Luiz Henrique Ribeiro de Oliveira</a> 
- <a href="https://github.com/marcofiap">Marco Aurélio Eberhardt Assimpção</a>
- <a href="https://github.com/PauloSenise">Paulo Henrique Senise</a> 


## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://github.com/Leoruiz197">Leonardo Ruiz Orabona</a>
### Coordenador(a)
- <a href="https://github.com/agodoi">André Godoi</a>



**Global Solution - 1º Semestre 2025 | FIAP**

Sistema IoT com Machine Learning para monitoramento em tempo real da potabilidade da água, desenvolvido para o desafio de eventos naturais extremos com foco em qualidade hídrica.

## 🎯 Objetivo

Desenvolver um sistema integrado que combina:
- **ESP32 com sensores** para coleta de dados em tempo real
- **Machine Learning** para classificação de potabilidade
- **Interface web moderna** para visualização e alertas
- **Banco de dados Oracle** para persistência histórica

## 🏗️ Arquitetura

### Padrão Arquitetural: Monolítico em Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (Streamlit)                 │
├─────────────────────────────────────────────────────────┤
│                  API/Controller Layer                   │
├─────────────────────────────────────────────────────────┤
│     Processing Layer    │    ML Model Layer             │
├─────────────────────────────────────────────────────────┤
│                 Persistence Layer (Oracle)              │
├─────────────────────────────────────────────────────────┤
│              Data Acquisition (ESP32/Wokwi)             │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principais

1. **Data Acquisition** (`servidor_local/`): Coleta dados via ESP32/Wokwi
2. **Data Processing** (`src/processing/`): Normalização e pré-processamento
3. **ML Model** (`src/model/`): Treinamento e inferência de potabilidade
4. **Persistence** (`src/persistence/`): Conexão Oracle e persistência
5. **API Controller** (`src/api/`): Orquestração do fluxo de dados
6. **User Interface** (`src/ui/`): Dashboard web com Streamlit
7. **Utils** (`src/utils/`): Logging e configurações
8. **Sensores** (`simularsensor/`): Simular sensores do Wokwi

## 🛠️ Tecnologias

- **Python 3.12+** - Linguagem principal
- **Scikit-learn** - Machine Learning (Random Forest)
- **Streamlit** - Interface web moderna
- **Oracle Database** - Persistência de dados
- **ESP32** - Microcontrolador IoT
- **Plotly** - Visualizações interativas
- **PyYAML** - Configurações
- **Pandas/NumPy** - Manipulação de dados
- **Wokwi** - Simulador de sensor ESP32

## 📋 Pré-requisitos

1. **Python 3.9+** instalado
2. **Oracle Database** configurado e rodando
3. **Git** para versionamento
4. **ESP32** ou simulador Wokwi (opcional para testes)

## 🚀 Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone git@github.com:marcofiap/GS1Sem.git
cd GS1Sem
```

### 2. Crie um ambiente virtual
```bash
python -m venv .venv

#mac
source .venv/bin/activate

#windows
.venv\Scripts\activate
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o Banco Oracle
Edite `config/config.yaml` com suas credenciais:
```yaml
database:
  user: "seu_usuario"
  password: "sua_senha"
  dsn: "localhost:1521/xe"
```

### 4. Treine o Modelo
```bash
python train_model.py
```

### 5. Execute a Aplicação
```bash
python run_app.py
```

### 6. Execute o servidor no mac
```bash
python src/api/servidor.py
```

### 6. Execute o servidor no windows
```bash
python -m src.api.servidor
```

### 7. Configure na pasta simularsensor/src a variável serverName dentro do arquivo main.cpp para setar o IP correto de sua máquina
Exemplo: String serverName = "http://192.168.2.166:8000/data"; 

### 8. Emule os sensores e clique no botão
A aplicação estará disponível em: http://localhost:8501

### 9. Para funcionar a análise em R pode ser preciso executar no seu terminal:
Rscript -e 'install.packages(c("ggplot2", "dplyr", "jsonlite"), repos = "https://cloud.r-project.org")'

## 📊 Como Adicionar Dados ao Sistema

Após a instalação, o banco de dados Oracle estará vazio. Para popular o sistema com dados para análise, você pode usar uma das seguintes opções:

### **Opção 1: Via Wokwi (Sensores Simulados)**
- Configure o simulador Wokwi conforme descrito no passo 7
- Ajuste o IP da sua máquina no arquivo `main.cpp`
- Execute os sensores virtuais no Wokwi
- Os dados são enviados via HTTP e salvos automaticamente no Oracle

### **Opção 2: Via Interface Web (Manual)**
- Acesse `http://localhost:8501` no navegador
- Navegue até a seção **"Análise Detalhada"**
- Insira valores manualmente para pH, turbidez, cloraminas e condutividade
- O sistema fará a predição usando Machine Learning
- Os dados podem ser salvos no banco para análise posterior

## 📊 Funcionalidades

### Dashboard Principal
- **Métricas em tempo real**: Total de leituras, % potabilidade, alertas
- **Gráficos interativos**: Tendências de pH, turbidez e outros parâmetros
- **Status atual**: Última leitura e classificação

### Análise Detalhada
- **Entrada manual** de parâmetros para análise
- **Predição ML** com nível de confiança
- **Análise de risco** por parâmetro individual
- **Recomendações** baseadas nos resultados

### Histórico
- **Visualização** de leituras históricas
- **Filtros** por período e tipo
- **Export** de dados em CSV
- **Estatísticas** agregadas

### Sistema de Alertas
- **Classificação** automática por severidade
- **Notificações** visuais para água não potável
- **Histórico** de alertas críticos

## 🔬 Machine Learning

### Modelo Utilizado
- **Algoritmo**: Random Forest Classifier
- **Features**: pH, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity
- **Target**: Potabilidade (0 = Não Potável, 1 = Potável)

### Performance
- **Acurácia esperada**: ~65-70% (dataset público)
- **Cross-validation**: 5-fold para validação robusta
- **Tratamento de desbalanceamento**: Class weights balanceados

### Pipeline de Dados
1. **Limpeza**: Tratamento de valores ausentes (mediana)
2. **Normalização**: StandardScaler para features numéricas
3. **Divisão**: 80% treino, 20% teste
4. **Validação**: Cross-validation e métricas detalhadas

## 🌐 Integração IoT

### ESP32 + Sensores
- **Sensor de pH**: Medição da acidez/alcalinidade
- **Sensor de Turbidez**: Claridade da água
- **Sensor de Cloro**: Nível de cloraminas

### Protocolo de Comunicação
```
ESP32 → HTTP GET → Servidor Local → Processamento → Oracle DB
```

### Exemplo de Requisição
```
GET /data?ph=7.2&turbidity=3.5&chloramines=1.2&conductivity=450
```

## 📁 Estrutura do Projeto

```
GS1Sem/
├── config/
│   └── config.yaml                    # Configurações do sistema
├── imagem/
│   ├── logo-fiap.png                  # Logo da FIAP
│   └── circuito.png                   # Imagem do circuito
├── include/
│   └── README                         # Documentação include
├── lib/
│   └── README                         # Documentação lib
├── logs/
│   └── app.log                        # Logs do sistema
├── simularsensor/                     # Simulador de sensores ESP32
│   ├── imagem/
│   │   └── circuito.png               # Imagem do circuito
│   ├── servidor_local/
│   │   └── servidor.py                # Servidor local para sensores
│   ├── src/
│   │   └── main.cpp                   # Código ESP32 (C++)
│   ├── .gitignore
│   ├── compile.bat                    # Script compilação Windows
│   ├── compile.sh                     # Script compilação Unix
│   ├── diagram.json                   # Diagrama Wokwi
│   ├── platformio.ini                 # Configurações PlatformIO
│   ├── README_SIMULADOR.md            # Documentação simulador
│   ├── requirements.txt               # Dependências simulador
│   └── wokwi.toml                     # Configurações Wokwi
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── controller.py              # Controller principal da API
│   │   └── servidor.py                # Servidor HTTP para sensores
│   ├── model/
│   │   ├── __init__.py
│   │   ├── predict.py                 # Inferência e predições
│   │   ├── train.py                   # Treinamento do modelo
│   │   └── water_quality_model.pkl    # Modelo treinado
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── db.py                      # Conexão Oracle e Repository
│   ├── processing/
│   │   ├── __init__.py
│   │   └── data_processor.py          # Processamento de dados
│   ├── r_analysis/                    # Análise estatística em R
│   │   ├── scripts/
│   │   │   └── water_analysis.R       # Script R para análise
│   │   ├── __init__.py
│   │   └── r_analyzer.py              # Interface Python-R
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py                     # Interface Streamlit
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py                 # Sistema de logging
│   └── __init__.py
├── tests/                             # Testes do sistema
│   ├── __init__.py
│   ├── 2water_quality_controller_test.py
│   ├── predictor_test_cases.py
│   ├── README
│   ├── water_quality_controller_test.py
│   ├── water_quality_predictor_test.py
│   └── WaterQualityModelTrainer_test.py
├── .gitignore                         # Arquivos ignorados pelo Git
├── __init__.py                        # Arquivo de inicialização
├── ANÁLISE_R_INSTRUÇÕES.md            # Instruções para análise R
├── debug_r_output.py                  # Debug de saídas R
├── README.md                          # Este arquivo
├── requirements.txt                   # Dependências Python
├── run_app.py                         # Script de execução principal
├── run_tests.py                       # Script para executar testes
├── test_r_analysis.py                 # Testes da análise R
├── test_r_streamlit.py                # Testes Streamlit com R
├── test_r_venv.py                     # Testes ambiente virtual R
├── train_model.py                     # Script de treinamento
└── water_potability.csv               # Dataset de treinamento
```

## 🔧 Configurações Avançadas

### Logging
O sistema gera logs estruturados em `logs/app.log` com níveis:
- **INFO**: Operações normais
- **ERROR**: Erros de sistema
- **WARNING**: Situações de atenção

### Cache
A UI utiliza cache para otimizar performance:
- **Estatísticas**: 60 segundos TTL
- **Leituras**: 30 segundos TTL
- **Alertas**: 30 segundos TTL

### Modelo de Dados Oracle
```sql
CREATE TABLE readings (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    timestamp TIMESTAMP,
    ph FLOAT,
    turbidity FLOAT,
    chloramines FLOAT,
    potability NUMBER(1)
);
```

## 🧪 Testes

### Executar Testes
```bash
python run_tests.py
```

### Tipos de Teste
- **Unit Tests**: Módulos individuais
- **Integration Tests**: Fluxo completo
- **Model Tests**: Validação do ML

## 📈 Monitoramento

### Métricas do Sistema
- **Uptime**: Disponibilidade da aplicação
- **Performance**: Tempo de resposta das predições
- **Accuracy**: Precisão do modelo em produção
- **Data Quality**: Validação dos dados de entrada

### Alertas Automáticos
- **pH crítico**: < 6.0 ou > 9.0
- **Turbidez alta**: > 25 NTU
- **Cloro inadequado**: < 0.1 ou > 4.0 ppm

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da Global Solution 2025.1 da FIAP.

---

**Desenvolvido com 💧 pela equipe FIAP GS 2025.1** 