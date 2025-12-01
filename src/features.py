import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_data(path: str) -> pd.DataFrame:
    """Load CSV data with error handling."""
    try:
        df = pd.read_csv(path)
        logger.info("Loaded %d rows, %d columns from %s", len(df), len(df.columns), path)
        return df
    except FileNotFoundError:
        logger.error("Data file not found: %s", path)
        raise
    except Exception as e:
        logger.error("Error loading data from %s: %s", path, str(e))
        raise

def preprocess(df: pd.DataFrame) -> tuple:
    """Preprocess data: extract features and target, handle missing values."""
    df = df.copy()
    if 'is_fraud' not in df.columns:
        raise ValueError("Dataset must contain 'is_fraud' column")
    
    X = df.drop(columns=['is_fraud'])
    y = df['is_fraud']

    # Log initial feature info
    n_numeric = len(X.select_dtypes(include=['number']).columns)
    n_non_numeric = len(X.columns) - n_numeric
    if n_non_numeric > 0:
        logger.info("Dropping %d non-numeric columns", n_non_numeric)

    # Extract numeric columns and fill NaN
    X = X.select_dtypes(include=['number']).fillna(0)
    logger.info("Features after preprocessing: %d numeric columns", X.shape[1])

    return X, y
