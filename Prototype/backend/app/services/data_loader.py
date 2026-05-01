"""Load and validate uploaded CSV for PCA anomaly detection."""

import io
from dataclasses import dataclass

import pandas as pd


@dataclass
class LoadResult:
    """Result of loading a CSV."""

    df: pd.DataFrame
    feature_columns: list[str]
    label_column: str | None  # If present, 0 = normal, 1 = anomaly
    n_rows: int
    n_features: int
    error: str | None = None


def load_and_validate_csv(
    content: bytes,
    filename: str,
    label_column: str | None = None,
    encoding: str = "utf-8",
) -> LoadResult:
    """
    Parse CSV, infer or use label column, and return numeric feature matrix.
    Drops non-numeric columns except the chosen label column.
    """
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=encoding, nrows=100_000)
    except Exception as e:
        return LoadResult(
            df=pd.DataFrame(),
            feature_columns=[],
            label_column=None,
            n_rows=0,
            n_features=0,
            error=f"Could not parse CSV: {e!s}",
        )

    if df.empty or len(df.columns) < 2:
        return LoadResult(
            df=pd.DataFrame(),
            feature_columns=[],
            label_column=None,
            n_rows=0,
            n_features=0,
            error="CSV must have at least 2 columns and some rows.",
        )

    # If label column specified, use it; otherwise look for common names
    if label_column and label_column in df.columns:
        pass
    elif "label" in df.columns:
        label_column = "label"
    elif "target" in df.columns:
        label_column = "target"
    elif "class" in df.columns:
        label_column = "class"
    else:
        label_column = None

    # Feature columns: numeric only, exclude label
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if label_column and label_column in numeric_cols:
        feature_columns = [c for c in numeric_cols if c != label_column]
    else:
        feature_columns = numeric_cols

    if not feature_columns:
        return LoadResult(
            df=df,
            feature_columns=[],
            label_column=label_column,
            n_rows=len(df),
            n_features=0,
            error="No numeric feature columns found.",
        )

    # Keep only feature columns + optional label for downstream use
    use_cols = feature_columns + ([label_column] if label_column else [])
    df_clean = df[use_cols].copy()

    # Drop rows with any NaN in features (or fill with median if preferred)
    df_clean = df_clean.dropna(subset=feature_columns)
    if df_clean.empty:
        return LoadResult(
            df=pd.DataFrame(),
            feature_columns=feature_columns,
            label_column=label_column,
            n_rows=0,
            n_features=len(feature_columns),
            error="No rows left after dropping missing values.",
        )

    return LoadResult(
        df=df_clean,
        feature_columns=feature_columns,
        label_column=label_column,
        n_rows=len(df_clean),
        n_features=len(feature_columns),
    )
