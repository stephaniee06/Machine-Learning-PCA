"""Per-row feature contribution to reconstruction error (which features make a point anomalous)."""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_feature_contributions(
    df: pd.DataFrame,
    feature_columns: list[str],
    label_column: str | None,
    n_components: int,
    threshold_percentile: float,
    top_k: int = 5,
) -> list[dict]:
    """
    Re-run PCA (same as pca_anomaly), then for each anomaly row compute
    per-feature squared residual (original - reconstructed)^2 and return
    top_k features that contributed most for that row.
    Returns list of dicts: one per row, with keys row_index, is_anomaly,
    reconstruction_error, top_features (list of {name, contribution}).
    """
    X = df[feature_columns].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if label_column is not None and label_column in df.columns:
        y = df[label_column].values.ravel()
        y_binary = np.where(y == 0, 0, 1) if np.unique(y).size <= 2 else (y != y.min()).astype(int)
        normal_mask = y_binary == 0
        X_fit = X_scaled[normal_mask]
    else:
        X_fit = X_scaled

    n_comp = min(n_components, X_fit.shape[1], X_fit.shape[0])
    pca = PCA(n_components=n_comp)
    pca.fit(X_fit)

    X_proj = pca.transform(X_scaled)
    X_reconstructed = pca.inverse_transform(X_proj)
    reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)

    if label_column is not None and normal_mask.any():
        thresh = np.percentile(reconstruction_error[normal_mask], threshold_percentile)
    else:
        thresh = np.percentile(reconstruction_error, threshold_percentile)

    is_anomaly = reconstruction_error > thresh
    # Per-feature squared residual (contribution to MSE * n_features = sum of squared residuals)
    squared_residuals = (X_scaled - X_reconstructed) ** 2  # (n_rows, n_features)

    out = []
    for i in range(len(df)):
        contribs = squared_residuals[i]
        order = np.argsort(contribs)[::-1]
        top = [
            {"name": feature_columns[j], "contribution": float(contribs[j])}
            for j in order[:top_k]
        ]
        out.append({
            "row_index": i,
            "is_anomaly": bool(is_anomaly[i]),
            "reconstruction_error": float(reconstruction_error[i]),
            "top_features": top,
        })
    return out
