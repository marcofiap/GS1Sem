import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import resample
import logging

class WaterDataProcessor:
    """Processador de dados de qualidade da água."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Quatro colunas que serão usadas como features:
        self.feature_columns = ['ph', 'Chloramines', 'Conductivity', 'Turbidity']
        # Nome da coluna-alvo numérica (deve ser 0/1)
        self.target_column = 'Potability'
        self.scaler_params = None

    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Carrega dados do arquivo CSV em um DataFrame."""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Dados carregados: {len(df)} registros")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e preprocessa os dados:
        - Se a coluna 'Potability' existir e contiver strings, mapeia:
            'Potável'    → 1
            'Suspeita'   → 0
            'Contaminada'→ 0
        - Preenche NaNs nas features e retorna apenas as 5 colunas:
          [ 'ph', 'Chloramines', 'Conductivity', 'Turbidity', 'Potability' ] (todas numéricas).
        """
        try:
            # 1) Se a coluna "Potability" existir como texto, faça o mapeamento direto:
            if 'Potability' in df.columns and df['Potability'].dtype == object:
                df = df.copy()
                df['Potability'] = df['Potability'].map({
                    'Potável': 1,
                    'Suspeita': 0,
                    'Contaminada': 0
                })
                # Agora df['Potability'] é 0/1, não mais texto

            # 2) Verificar se as colunas obrigatórias existem
            missing_cols = set(self.feature_columns + [self.target_column]) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Colunas faltando: {missing_cols}")

            # 3) Selecionar apenas as colunas de interesse
            df_clean = df[self.feature_columns + [self.target_column]].copy()

            # 4) Log de quantos NaNs existem antes de preencher
            missing_before = df_clean.isnull().sum().sum()
            self.logger.info(f"Valores ausentes antes da limpeza: {missing_before}")

            # 5) Remover linhas cuja Potability ainda seja NaN (caso alguma não tenha sido mapeada)
            df_clean = df_clean.dropna(subset=[self.target_column])

            # 6) Preencher NaNs nas features com a mediana
            for col in self.feature_columns:
                n_missing = df_clean[col].isnull().sum()
                if n_missing > 0:
                    median_value = df_clean[col].median()
                    df_clean = df_clean.copy()
                    df_clean[col] = df_clean[col].fillna(median_value)
                    self.logger.info(
                        f"Preenchidos {n_missing} valores ausentes em '{col}' com mediana {median_value:.2f}")

            # 7) Log de quantos NaNs ainda restam após preencher (esperamos zero)
            missing_after = df_clean.isnull().sum().sum()
            self.logger.info(f"Valores ausentes após limpeza: {missing_after}")
            self.logger.info(f"Registros finais após limpeza: {len(df_clean)}")

            return df_clean

        except Exception as e:
            self.logger.error(f"Erro na limpeza dos dados: {e}")
            raise

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera um resumo estatístico do DataFrame limpo.
        Espera que 'Potability' seja 0/1, então soma pode ser convertida em int.
        """
        try:
            summary = {
                'total_records': len(df),
                'potable_count': int(df[self.target_column].sum()),
                'non_potable_count': int(len(df) - df[self.target_column].sum()),
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

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Extrai X (features) e y (target) para treinamento."""
        try:
            available_features = [col for col in self.feature_columns if col in df.columns]
            if not available_features:
                raise ValueError("Nenhuma feature encontrada no dataset")

            self.logger.info(f"Features utilizadas: {available_features}")
            X = df[available_features].values
            y = df[self.target_column].values  # já é 0/1
            return X, y

        except Exception as e:
            self.logger.error(f"Erro na preparação das features: {e}")
            raise

    def split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Divide dados em treino e teste, mantendo proporção das classes (stratify=y)."""
        try:
            self.logger.info(f"Dividindo dados - Test size: {test_size}")
            unique, counts = np.unique(y, return_counts=True)
            dist = dict(zip(unique, counts))
            self.logger.info(f"Distribuição de classes (antes do split): {dist}")

            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=random_state,
                stratify=y
            )
            self.logger.info(f"Amostras de treino: {X_train.shape[0]}")
            self.logger.info(f"Amostras de teste: {X_test.shape[0]}")
            return X_train, X_test, y_train, y_test

        except Exception as e:
            self.logger.error(f"Erro na divisão dos dados: {e}")
            raise

    def normalize_features(self, X_train: np.ndarray, X_test: np.ndarray = None
                           ) -> Tuple[np.ndarray, np.ndarray]:
        """Aplica normalização (z-score) às features."""
        try:
            self.logger.info("Normalizando features")
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            self.scaler_params = {'mean': mean, 'std': std}

            X_train_scaled = (X_train - mean) / std
            X_test_scaled = None
            if X_test is not None:
                X_test_scaled = (X_test - mean) / std

            self.logger.info(f"Features normalizadas (treino): {X_train_scaled.shape}")
            if X_test_scaled is not None:
                self.logger.info(f"Features normalizadas (teste): {X_test_scaled.shape}")
            return X_train_scaled, X_test_scaled

        except Exception as e:
            self.logger.error(f"Erro na normalização: {e}")
            raise

    def process_sensor_reading(self, reading: Dict[str, Any]) -> np.ndarray:
        """Processa uma única leitura de sensor e retorna array 1×4 normalizado."""
        try:
            features = []
            for col in self.feature_columns:
                # aceita chaves minúsculas ou com case
                if col.lower() in reading:
                    features.append(float(reading[col.lower()]))
                elif col in reading:
                    features.append(float(reading[col]))
                else:
                    self.logger.warning(f"Feature de sensor '{col}' não encontrada; atribuindo 0.0")
                    features.append(0.0)

            features_array = np.array(features).reshape(1, -1)
            if self.scaler_params:
                mean = self.scaler_params['mean']
                std = self.scaler_params['std']
                features_array = (features_array - mean) / std
            return features_array

        except Exception as e:
            self.logger.error(f"Erro no processamento da leitura: {e}")
            raise

    def get_feature_names(self):
        """Retorna lista de nomes das features."""
        return self.feature_columns.copy()

    def get_target_name(self):
        """Retorna nome da coluna target."""
        return self.target_column
