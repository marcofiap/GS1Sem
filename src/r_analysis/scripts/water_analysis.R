
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
  
  cat("Análise concluída. Resultados salvos em:", output_dir, "
")
}

# Executar análise se chamado diretamente
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 2) {
  analyze_water_data(args[1], args[2])
}
