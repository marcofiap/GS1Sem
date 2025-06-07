# 📊 Análises Estatísticas em R - Instruções de Uso

## 🎯 **Visão Geral**

O sistema agora inclui **análises estatísticas avançadas em R** integradas à interface Streamlit, permitindo análises detalhadas dos dados de qualidade da água usando as melhores práticas estatísticas.

## 📋 **Tipos de Análises Implementadas**

### 🔢 **Medidas de Tendência Central**
- **Média**: Valor médio dos dados
- **Mediana**: Valor central quando dados estão ordenados
- **Moda**: Valor mais frequente

### 📐 **Medidas de Dispersão**
- **Variância**: Medida de dispersão dos dados
- **Desvio Padrão**: Raiz quadrada da variância
- **Amplitude**: Diferença entre maior e menor valor
- **IQR (Intervalo Interquartil)**: Diferença entre Q3 e Q1

### 📊 **Medidas Separatrizes**
- **Quartis**: Q1 (25%), Q2 (50%), Q3 (75%)
- **Decis**: Divisão dos dados em 10 partes iguais

## 📈 **Gráficos Gerados**

### 📉 **Para Variáveis Quantitativas**
- **Histograma**: Distribuição de frequências
- **Boxplot**: Visualização de quartis e outliers

### 📊 **Para Variáveis Qualitativas**
- **Gráfico de Barras**: Distribuição de potabilidade

## 🛠️ **Pré-requisitos**

### 1. **Instalação do R**
```bash
# Windows: Baixe o instalador
https://cran.r-project.org/bin/windows/base/

# Ubuntu/Debian
sudo apt update
sudo apt install r-base

# macOS com Homebrew
brew install r
```

### 2. **Verificar Instalação**
```bash
# No terminal/prompt de comando
Rscript --version
```

### 3. **Pacotes R (Instalados Automaticamente)**
- `ggplot2` - Gráficos avançados
- `dplyr` - Manipulação de dados
- `jsonlite` - Manipulação JSON

## 🚀 **Como Usar**

### 1. **Executar o Sistema**
```bash
# Terminal 1 - Servidor API
python -m src.api.servidor

# Terminal 2 - Interface Streamlit
python run_app.py
```

### 2. **Acessar Interface Web**
- Abra o navegador em: `http://localhost:8501`
- Navegue para: **Análise em R** (última opção do menu)

### 3. **Escolher Fonte dos Dados**

#### 📊 **Dados Pré-carregados**
- Usa o dataset `water_potability.csv`
- 3.276 registros históricos
- 10 variáveis de qualidade da água

#### ⏰ **Dados em Tempo Real**
- Usa dados coletados pelos sensores ESP32
- Dados atualizados dinamicamente
- Configurações avançadas disponíveis

### 4. **Configurar Análise**
1. **Selecionar variáveis** para análise
2. **Escolher tipos de análise** desejados
3. **Configurar parâmetros** (se necessário)
4. **Executar análises** com o botão

## 📊 **Exemplo de Uso**

### **Cenário: Análise de pH**

1. **Selecione** a variável `ph`
2. **Marque** todas as opções de análise
3. **Execute** a análise
4. **Visualize** os resultados:

```
📈 pH
Tendência Central:
├── Média: 7.0808
├── Mediana: 7.0365
└── Moda: 6.5234

Dispersão:
├── Variância: 1.5948
├── Desvio Padrão: 1.2629
├── Amplitude: 9.0509
└── IQR: 1.5656

Separatrizes:
├── Q1: 6.0934
├── Q2: 7.0365
└── Q3: 7.6590
```

## 🔧 **Teste de Funcionamento**

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_r_analysis.py
```

### **Saída Esperada:**
```
🚀 Iniciando Testes do Módulo R
============================================================
🧪 Testando Módulo de Análise R
==================================================
1. Verificando disponibilidade do R...
✅ R está disponível!

2. Verificando/instalando pacotes R...
✅ Pacotes R instalados com sucesso!

3. Criando dados de teste...
✅ Dados criados: 100 registros, 10 variáveis

4. Executando análise R...
✅ Análise executada com sucesso!

5. Verificando resultados...
   - Estatísticas para 9 variáveis
   - 19 gráficos gerados

✅ Teste concluído com sucesso!

🌊 Testando com Dataset Real
==================================================
✅ Dataset encontrado!
📊 Dataset carregado: 3276 registros
📋 Usando amostra de 200 registros
✅ Análise do dataset real concluída!

🎉 TODOS OS TESTES PASSARAM!
```

## ⚠️ **Solução de Problemas**

### **Erro: "R não está disponível"**
1. Verifique se R está instalado
2. Adicione R ao PATH do sistema
3. Reinicie o terminal/aplicação

### **Erro: "Pacotes R não instalados"**
1. Execute manualmente no R:
```r
install.packages(c("ggplot2", "dplyr", "jsonlite"))
```

### **Erro: "Timeout na execução"**
- Dados muito grandes - use amostra menor
- Verifique recursos do sistema

### **Nenhum dado encontrado**
1. Verifique se o servidor está rodando
2. Configure o simulador ESP32
3. Envie alguns dados de teste

## 🏗️ **Arquitetura Técnica**

```
src/r_analysis/
├── __init__.py          # Módulo principal
├── r_analyzer.py        # Classe Python que executa R
└── scripts/
    └── water_analysis.R # Script R para análises
```

### **Fluxo de Execução:**
1. **Python** (Streamlit) → recebe dados
2. **RAnalyzer** → prepara dados e executa script R
3. **R Script** → calcula estatísticas e gera gráficos
4. **Python** → recebe resultados e exibe na interface

## 📋 **Variáveis Disponíveis**

### **Dataset Pré-carregado:**
- `ph` - Potencial hidrogeniônico
- `Hardness` - Dureza da água
- `Solids` - Sólidos totais dissolvidos
- `Chloramines` - Cloraminas
- `Sulfate` - Sulfatos
- `Conductivity` - Condutividade
- `Organic_carbon` - Carbono orgânico
- `Trihalomethanes` - Trihalometanos
- `Turbidity` - Turbidez
- `Potability` - Potabilidade (0=Não, 1=Sim)

### **Dados em Tempo Real:**
- `ph` - pH medido pelo sensor
- `turbidity` - Turbidez medida
- `chloramines` - Cloraminas detectadas
- `potability` - Classificação do modelo

## 🎯 **Próximos Passos**

1. ✅ **Análises básicas implementadas**
2. 🔄 **Análises de correlação** (próxima versão)
3. 🔄 **Testes de normalidade** (próxima versão)
4. 🔄 **Análise de séries temporais** (próxima versão)
5. 🔄 **Modelos preditivos avançados** (próxima versão)

---

**🎉 Parabéns! Seu sistema agora tem análises estatísticas profissionais em R integradas!** 