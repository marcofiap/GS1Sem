####################################
##### Arquivo: data_processor.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
import logging

class WaterDataProcessor:
    """Processador de dados de qualidade da água"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feature_columns = [
            'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
            'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
        ]
        self.target_column = 'Potability'
        self.scaler_params = None
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Carrega dados do arquivo CSV"""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Dados carregados: {len(df)} registros")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e preprocessa os dados"""
        try:
            # Verificar colunas necessárias
            missing_cols = set(self.feature_columns + [self.target_column]) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Colunas faltando: {missing_cols}")
            
            # Criar cópia para processamento
            df_clean = df[self.feature_columns + [self.target_column]].copy()
            
            # Log valores ausentes antes da limpeza
            missing_before = df_clean.isnull().sum().sum()
            self.logger.info(f"Valores ausentes antes da limpeza: {missing_before}")
            
            # Remover linhas com target ausente
            df_clean = df_clean.dropna(subset=[self.target_column])
            
            # Preencher valores ausentes nas features com a mediana
            for col in self.feature_columns:
                if df_clean[col].isnull().sum() > 0:
                    median_value = df_clean[col].median()
                    # Corrigir warning do pandas
                    df_clean = df_clean.copy()
                    df_clean[col] = df_clean[col].fillna(median_value)
                    self.logger.info(f"Preenchidos valores ausentes em {col} com mediana {median_value:.2f}")
            
            # Log valores ausentes após limpeza
            missing_after = df_clean.isnull().sum().sum()
            self.logger.info(f"Valores ausentes após limpeza: {missing_after}")
            self.logger.info(f"Registros finais: {len(df_clean)}")
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza dos dados: {e}")
            raise
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara features e target para treinamento"""
        try:
            # Selecionar apenas as colunas de features disponíveis
            available_features = [col for col in self.feature_columns if col in df.columns]
            
            if not available_features:
                raise ValueError("Nenhuma feature encontrada no dataset")
            
            self.logger.info(f"Features utilizadas: {available_features}")
            
            X = df[available_features].values
            y = df[self.target_column].values if self.target_column in df.columns else None
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Erro na preparação das features: {e}")
            raise
    
    def split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Divide dados em treino e teste"""
        try:
            self.logger.info(f"Dividindo dados - Test size: {test_size}")
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            self.logger.info(f"Treino: {X_train.shape[0]} amostras")
            self.logger.info(f"Teste: {X_test.shape[0]} amostras")
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            self.logger.error(f"Erro na divisão dos dados: {e}")
            raise
    
    def normalize_features(self, X_train: np.ndarray, X_test: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """Normaliza features usando z-score"""
        try:
            self.logger.info("Normalizando features")
            
            # Calcular parâmetros de normalização dos dados de treino
            self.scaler_params = {
                'mean': np.mean(X_train, axis=0),
                'std': np.std(X_train, axis=0)
            }
            
            # Normalizar dados de treino
            X_train_scaled = (X_train - self.scaler_params['mean']) / self.scaler_params['std']
            
            # Normalizar dados de teste se fornecidos
            X_test_scaled = None
            if X_test is not None:
                X_test_scaled = (X_test - self.scaler_params['mean']) / self.scaler_params['std']
            
            self.logger.info(f"Features normalizadas - Train: {X_train_scaled.shape}")
            if X_test_scaled is not None:
                self.logger.info(f"Features normalizadas - Test: {X_test_scaled.shape}")
            
            return X_train_scaled, X_test_scaled
            
        except Exception as e:
            self.logger.error(f"Erro na normalização: {e}")
            raise
    
    def process_sensor_reading(self, reading: Dict[str, Any]) -> np.ndarray:
        """Processa uma leitura individual do sensor"""
        try:
            # Extrair features da leitura
            features = []
            for col in self.feature_columns:
                if col.lower() in reading:
                    features.append(float(reading[col.lower()]))
                elif col in reading:
                    features.append(float(reading[col]))
                else:
                    # Usar valor padrão se feature não encontrada
                    # Log apenas para features críticas do sensor
                    if col.lower() in ['ph', 'turbidity', 'chloramines', 'conductivity']:
                        self.logger.warning(f"Feature de sensor {col} não encontrada na leitura")
                    features.append(0.0)
            
            # Converter para array numpy
            features_array = np.array(features).reshape(1, -1)
            
            # Normalizar usando parâmetros salvos
            if self.scaler_params:
                features_array = (features_array - self.scaler_params['mean']) / self.scaler_params['std']
            
            return features_array
            
        except Exception as e:
            self.logger.error(f"Erro no processamento da leitura: {e}")
            raise
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Retorna resumo estatístico dos dados"""
        try:
            summary = {
                'total_records': len(df),
                'potable_count': int(df[self.target_column].sum()) if self.target_column in df.columns else 0,
                'non_potable_count': len(df) - int(df[self.target_column].sum()) if self.target_column in df.columns else 0,
                'feature_stats': {}
            }
            
            for col in self.feature_columns:
                if col in df.columns:
                    summary['feature_stats'][col] = {
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'missing': int(df[col].isnull().sum())
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro na geração do resumo: {e}")
            raise
    
    def get_feature_names(self):
        """Retorna nomes das features"""
        return self.feature_columns.copy()
    
    def get_target_name(self):
        """Retorna nome da coluna target"""
        return self.target_column 