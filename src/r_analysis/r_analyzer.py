####################################
##### Arquivo: r_analyzer.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import pandas as pd
import subprocess
import json
import tempfile
import os
from pathlib import Path
import base64
from typing import Dict, List, Any, Optional
from ..utils.logging import get_logger

logger = get_logger(__name__)

class RAnalyzer:
    """Classe para executar análises estatísticas em R."""
    
    def __init__(self):
        self.r_script_path = Path(__file__).parent / "scripts"
        self.r_script_path.mkdir(exist_ok=True)
        self.rscript_path = None  # Será definido ao verificar disponibilidade
        self._r_availability_checked = False  # Flag para evitar verificações repetidas
        self._create_r_scripts()
    
    def _create_r_scripts(self):
        """Cria os scripts R necessários para as análises."""
        
        # Script para análises estatísticas
        analysis_script = '''
# Análises Estatísticas para Qualidade da Água
library(ggplot2)
library(dplyr)
library(jsonlite)

# Função para medidas de tendência central
calc_central_tendency <- function(x) {
  list(
    media = mean(x, na.rm = TRUE),
    mediana = median(x, na.rm = TRUE),
    moda = as.numeric(names(sort(table(x), decreasing = TRUE))[1])
  )
}

# Função para medidas de dispersão
calc_dispersion <- function(x) {
  list(
    variancia = var(x, na.rm = TRUE),
    desvio_padrao = sd(x, na.rm = TRUE),
    amplitude = max(x, na.rm = TRUE) - min(x, na.rm = TRUE),
    iqr = IQR(x, na.rm = TRUE)
  )
}

# Função para quartis e decis
calc_separatrizes <- function(x) {
  list(
    quartis = quantile(x, probs = c(0.25, 0.5, 0.75), na.rm = TRUE),
    decis = quantile(x, probs = seq(0.1, 0.9, 0.1), na.rm = TRUE)
  )
}

# Função principal de análise
analyze_water_data <- function(data_file, output_dir) {
  # Ler dados
  data <- read.csv(data_file)
  
  # Criar diretório de saída
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  
  # Identificar variáveis numéricas
  numeric_vars <- names(data)[sapply(data, is.numeric)]
  
  results <- list()
  
  # Análises para cada variável numérica
  for (var in numeric_vars) {
    if (var == "potability") next  # Pular variável target
    
    var_data <- data[[var]]
    var_data <- var_data[!is.na(var_data)]  # Remover NAs
    
    if (length(var_data) == 0) next
    
    # Calcular estatísticas
    results[[var]] <- list(
      tendencia_central = calc_central_tendency(var_data),
      dispersao = calc_dispersion(var_data),
      separatrizes = calc_separatrizes(var_data)
    )
    
    # Criar histograma
    p1 <- ggplot(data, aes_string(x = var)) +
      geom_histogram(bins = 30, fill = "steelblue", alpha = 0.7) +
      labs(title = paste("Histograma -", var),
           x = var,
           y = "Frequência") +
      theme_minimal()
    
    ggsave(file.path(output_dir, paste0("histogram_", var, ".png")), 
           plot = p1, width = 8, height = 6, dpi = 300)
    
    # Criar boxplot
    p2 <- ggplot(data, aes_string(y = var)) +
      geom_boxplot(fill = "lightblue", alpha = 0.7) +
      labs(title = paste("Boxplot -", var),
           y = var) +
      theme_minimal()
    
    ggsave(file.path(output_dir, paste0("boxplot_", var, ".png")), 
           plot = p2, width = 8, height = 6, dpi = 300)
  }
  
  # Gráfico de barras para potabilidade
  if ("potability" %in% names(data)) {
    potability_counts <- table(data$potability)
    potability_df <- data.frame(
      potability = factor(names(potability_counts), levels = c("0", "1"), 
                         labels = c("Não Potável", "Potável")),
      count = as.numeric(potability_counts)
    )
    
    p3 <- ggplot(potability_df, aes(x = potability, y = count, fill = potability)) +
      geom_bar(stat = "identity", alpha = 0.8) +
      scale_fill_manual(values = c("Não Potável" = "red", "Potável" = "green")) +
      labs(title = "Distribuição de Potabilidade",
           x = "Potabilidade",
           y = "Contagem") +
      theme_minimal() +
      theme(legend.position = "none")
    
    ggsave(file.path(output_dir, "barplot_potability.png"), 
           plot = p3, width = 8, height = 6, dpi = 300)
  }
  
  # Salvar resultados estatísticos
  write_json(results, file.path(output_dir, "statistics.json"), 
             pretty = TRUE, auto_unbox = TRUE)
  
  cat("Análise concluída. Resultados salvos em:", output_dir, "\n")
}

# Executar análise se chamado diretamente
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 2) {
  analyze_water_data(args[1], args[2])
}
'''
        
        script_file = self.r_script_path / "water_analysis.R"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(analysis_script)
        
        logger.info(f"Script R criado em: {script_file}")
    
    def analyze_data(self, data: pd.DataFrame, analysis_type: str = "complete") -> Dict[str, Any]:
        """
        Executa análise estatística nos dados usando R.
        
        Args:
            data: DataFrame com os dados para análise
            analysis_type: Tipo de análise ('complete', 'descriptive', 'graphics')
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Verificar se R está disponível
            if not self.check_r_availability():
                return {"error": "R não está disponível no sistema"}
            
            # Criar arquivo temporário para os dados
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_data:
                data.to_csv(temp_data.name, index=False)
                data_file = temp_data.name
            
            # Criar diretório temporário para resultados
            with tempfile.TemporaryDirectory() as temp_output:
                # Executar script R
                script_path = self.r_script_path / "water_analysis.R"
                
                # Usar o caminho do R descoberto
                rscript_cmd = self.rscript_path
                cmd = [rscript_cmd, str(script_path), data_file, temp_output]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    logger.error(f"Erro na execução do R: {result.stderr}")
                    return {"error": f"Erro na execução do R: {result.stderr}"}
                
                # Ler resultados estatísticos
                stats_file = os.path.join(temp_output, "statistics.json")
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        statistics = json.load(f)
                else:
                    statistics = {}
                
                # Ler gráficos
                graphics = {}
                for file in os.listdir(temp_output):
                    if file.endswith('.png'):
                        file_path = os.path.join(temp_output, file)
                        with open(file_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                            graphics[file.replace('.png', '')] = img_data
                
                # Limpar arquivo temporário
                os.unlink(data_file)
                
                return {
                    "success": True,
                    "statistics": statistics,
                    "graphics": graphics,
                    "r_output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na execução do R")
            return {"error": "Timeout na execução do script R"}
        except Exception as e:
            logger.error(f"Erro na análise R: {str(e)}")
            return {"error": f"Erro na análise: {str(e)}"}
    
    def check_r_availability(self, force_recheck: bool = False) -> bool:
        """Verifica se R está disponível no sistema."""
        
        # Se já verificamos e encontramos, não verificar novamente (a menos que forçado)
        if self._r_availability_checked and self.rscript_path and not force_recheck:
            return True
        
        # Lista de possíveis localizações do Rscript no Windows
        possible_paths = [
            'Rscript',  # Se estiver no PATH
            r'C:\Program Files\R\R-4.4.2\bin\Rscript.exe',
            r'C:\Program Files\R\R-4.4.1\bin\Rscript.exe', 
            r'C:\Program Files\R\R-4.4.0\bin\Rscript.exe',
            r'C:\Program Files\R\R-4.3.3\bin\Rscript.exe',
            r'C:\Program Files\R\R-4.3.2\bin\Rscript.exe',
            r'C:\Program Files\R\R-4.3.1\bin\Rscript.exe',
            r'C:\Program Files\R\R-4.3.0\bin\Rscript.exe',
            r'C:\Program Files (x86)\R\R-4.4.2\bin\Rscript.exe',
            r'C:\Program Files (x86)\R\R-4.4.1\bin\Rscript.exe',
            r'C:\Program Files (x86)\R\R-4.4.0\bin\Rscript.exe',
        ]
        
        # Tentar encontrar R automaticamente
        import glob
        r_program_files = glob.glob(r'C:\Program Files\R\R-*\bin\Rscript.exe')
        r_program_files_x86 = glob.glob(r'C:\Program Files (x86)\R\R-*\bin\Rscript.exe')
        possible_paths.extend(r_program_files)
        possible_paths.extend(r_program_files_x86)
        
        for rscript_path in possible_paths:
            try:
                result = subprocess.run([rscript_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Salvar o caminho encontrado para uso futuro
                    self.rscript_path = rscript_path
                    self._r_availability_checked = True
                    logger.info(f"R encontrado em: {rscript_path}")
                    return True
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        self._r_availability_checked = True
        logger.error("R não encontrado em nenhuma localização padrão")
        return False
    
    def install_required_packages(self) -> bool:
        """Instala pacotes R necessários."""
        # Verificar se R está disponível primeiro
        if not self.check_r_availability():
            logger.error("R não está disponível - impossível instalar pacotes")
            return False
            
        packages = ['ggplot2', 'dplyr', 'jsonlite']
        
        # Usar o caminho do R descoberto
        rscript_cmd = self.rscript_path if self.rscript_path else 'Rscript'
        
        for package in packages:
            try:
                cmd = [rscript_cmd, '-e', f'if (!require({package})) install.packages("{package}", repos="https://cran.r-project.org")']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    logger.error(f"Falha ao instalar pacote R: {package}")
                    logger.error(f"Erro: {result.stderr}")
                    return False
                    
            except Exception as e:
                logger.error(f"Erro ao instalar pacote {package}: {str(e)}")
                return False
        
        return True

    def _reset_r_detection(self):
        """Força nova detecção do R (útil para problemas de cache)."""
        self.rscript_path = None
        self._r_availability_checked = False 