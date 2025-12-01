import sys
import argparse
import logging
import mlflow
from mlflow import sklearn as mlflow_sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score

from features import load_data, preprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def train(args):
    """Train a RandomForest model and log to MLflow."""
    try:
        logger.info("Training model with data from %s", args.data_path)
        mlflow.set_tracking_uri(args.mlflow_uri)
        mlflow.set_experiment(args.experiment_name)
        df = load_data(args.data_path)
        logger.info("Data loaded: %d rows", len(df))
        X, y = preprocess(df)
        logger.info("Features: %d, Samples: %d", X.shape[1], X.shape[0])
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        logger.info("Train/Val split: %d / %d", len(X_train), len(X_val))
        with mlflow.start_run() as run:
            n_estimators = args.n_estimators
            max_depth = args.max_depth
            logger.info("Training RandomForest: n_estimators=%d, max_depth=%d", n_estimators, max_depth)
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            
            # Use predict_proba if available for AUC, else fallback
            if hasattr(model, "predict_proba"):
                preds = model.predict_proba(X_val)[:, 1]
            else:
                preds = model.predict(X_val)
            
            auc = float(roc_auc_score(y_val, preds))
            acc = float(accuracy_score(y_val, model.predict(X_val)))
            logger.info("Validation metrics - AUC: %.4f, Accuracy: %.4f", auc, acc)
            
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_metric("val_auc", auc)
            mlflow.log_metric("val_accuracy", acc)
            mlflow_sklearn.log_model(model, "model")
            logger.info("Model logged to MLflow run %s", run.info.run_id)
            print(f"✓ Training complete. AUC: {auc:.4f}, Accuracy: {acc:.4f}")
            print(f"  Use MODEL_URI='runs:/{run.info.run_id}/model' in inference.")
    except Exception as e:
        logger.error("Training failed: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train fraud detection model with MLflow tracking')
    parser.add_argument('--data-path', default='data/transactions.csv', help='Path to CSV data file')
    parser.add_argument('--mlflow-uri', default='http://localhost:5000', help='MLflow server URI')
    parser.add_argument('--experiment-name', default='local_exp', help='MLflow experiment name')
    parser.add_argument('--n-estimators', type=int, default=50, dest='n_estimators', help='Number of trees in forest')
    parser.add_argument('--max-depth', type=int, default=6, help='Maximum tree depth')
    args = parser.parse_args()
    train(args)
