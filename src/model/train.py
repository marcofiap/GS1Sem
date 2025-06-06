####################################
##### Arquivo: train.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from ..processing.data_processor import WaterDataProcessor
from ..utils.logging import get_logger, setup_logging
import yaml

# Configurar logging
setup_logging()
logger = get_logger(__name__)

class WaterQualityModelTrainer:
    """Classe responsável pelo treinamento do modelo de qualidade da água."""
    
    def __init__(self):
        self.processor = WaterDataProcessor()
        self.model = None
        self.model_path = None
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações do arquivo YAML."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        self.model_path = config['ml']['model_path']
    
    def train_model(self, csv_path: str):
        """Treina o modelo de classificação de qualidade da água."""
        logger.info("Iniciando treinamento do modelo")
        
        # 1. Carregar e processar dados
        df = self.processor.load_csv_data(csv_path)
        if df.empty:
            raise ValueError("Não foi possível carregar dados do CSV")
        
        # 2. Limpar dados
        df_clean = self.processor.clean_data(df)
        
        # 3. Preparar features e target
        X, y = self.processor.prepare_features(df_clean)
        
        # 4. Dividir dados
        X_train, X_test, y_train, y_test = self.processor.split_data(X, y)
        
        # 5. Normalizar features
        X_train_scaled, X_test_scaled = self.processor.normalize_features(X_train, X_test)
        
        # 6. Treinar modelo
        logger.info("Treinando modelo Random Forest")
        
        # Configurar modelo com hiperparâmetros otimizados
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'  # Para lidar com possível desbalanceamento
        )
        
        # Treinar modelo
        self.model.fit(X_train_scaled, y_train)
        
        # 7. Avaliar modelo
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Acurácia no treino: {train_score:.4f}")
        logger.info(f"Acurácia no teste: {test_score:.4f}")
        
        # 8. Predições e métricas detalhadas
        y_pred = self.model.predict(X_test_scaled)
        
        logger.info("\nRelatório de Classificação:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        logger.info("\nMatriz de Confusão:")
        logger.info(f"\n{confusion_matrix(y_test, y_pred)}")
        
        # 9. Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        logger.info(f"Cross-validation scores: {cv_scores}")
        logger.info(f"CV Score médio: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # 10. Importância das features
        feature_importance = self.model.feature_importances_
        feature_names = self.processor.feature_columns
        
        logger.info("\nImportância das Features:")
        for name, importance in zip(feature_names, feature_importance):
            logger.info(f"{name}: {importance:.4f}")
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_scores': cv_scores,
            'feature_importance': dict(zip(feature_names, feature_importance))
        }
    
    def optimize_hyperparameters(self, X_train, y_train):
        """Otimiza hiperparâmetros usando Grid Search."""
        logger.info("Otimizando hiperparâmetros")
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42, class_weight='balanced')
        
        grid_search = GridSearchCV(
            rf, param_grid, cv=3, 
            scoring='accuracy', n_jobs=-1, 
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Melhores parâmetros: {grid_search.best_params_}")
        logger.info(f"Melhor score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def save_model(self):
        """Salva o modelo treinado e o processor."""
        if self.model is None:
            raise ValueError("Modelo não foi treinado ainda")
        
        # Criar diretório se não existir
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar modelo e processor juntos
        model_data = {
            'model': self.model,
            'processor': self.processor
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Modelo salvo em: {self.model_path}")
    
    def get_data_insights(self, csv_path: str):
        """Gera insights sobre os dados."""
        df = self.processor.load_csv_data(csv_path)
        df_clean = self.processor.clean_data(df)
        summary = self.processor.get_data_summary(df_clean)
        
        logger.info("=== INSIGHTS DOS DADOS ===")
        logger.info(f"Total de registros: {summary['total_records']}")
        logger.info(f"Água potável: {summary['potable_count']} ({summary['potable_count']/summary['total_records']*100:.1f}%)")
        logger.info(f"Água não potável: {summary['non_potable_count']} ({summary['non_potable_count']/summary['total_records']*100:.1f}%)")
        
        logger.info("\n=== ESTATÍSTICAS DAS FEATURES ===")
        for feature, stats in summary['feature_stats'].items():
            logger.info(f"{feature}: μ={stats['mean']:.2f}, σ={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
        
        return summary

def main():
    """Função principal para treinamento do modelo."""
    logger.info("=== INICIANDO TREINAMENTO DO MODELO ===")
    
    # Caminho do CSV de dados
    csv_path = Path(__file__).parent.parent.parent / "water_potability.csv"
    
    if not csv_path.exists():
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        return
    
    trainer = WaterQualityModelTrainer()
    
    try:
        # Gerar insights dos dados
        trainer.get_data_insights(str(csv_path))
        
        # Treinar modelo
        results = trainer.train_model(str(csv_path))
        
        # Salvar modelo
        trainer.save_model()
        
        logger.info("=== TREINAMENTO CONCLUÍDO COM SUCESSO ===")
        logger.info(f"Acurácia final no teste: {results['test_accuracy']:.4f}")
        
    except Exception as e:
        logger.error(f"Erro durante o treinamento: {e}")
        raise

if __name__ == "__main__":
    main() 