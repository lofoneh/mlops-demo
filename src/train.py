import os
import argparse
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score

from features import load_data, preprocess

def train(args):
    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.set_experiment(args.experiment_name)
    df = load_data(args.data_path)
    X, y = preprocess(df)
    X_train, X_val, y_train, y_val = train_test_split(X,y,test_size=0.2,random_state=42)
    with mlflow.start_run():
        n_estimators = args.n_estimators
        max_depth = args.max_depth
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:,1] if hasattr(model, "predict_proba") else model.predict(X_val)
        auc = roc_auc_score(y_val, preds)
        acc = accuracy_score(y_val, model.predict(X_val))
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_metric("val_auc", auc)
        mlflow.log_metric("val_acc", acc)
        mlflow.sklearn.log_model(model, "model")
        print("Run completed. val_auc:", auc)
        print("To use this model in inference, set MODEL_URI to 'runs:/{run_id}/model' or register it in Model Registry.")
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', default='data/transactions.csv')
    parser.add_argument('--mlflow-uri', default='http://localhost:5000')
    parser.add_argument('--experiment-name', default='local_exp')
    parser.add_argument('--n-estimators', type=int, default=50)
    parser.add_argument('--max-depth', type=int, default=6)
    args = parser.parse_args()
    train(args)
