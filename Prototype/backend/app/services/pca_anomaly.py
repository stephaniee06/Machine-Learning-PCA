"""PCA-based anomaly detection: fit on normal (or all) data, score by reconstruction error."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass
class PCAAnomalyResult:
    """Result of PCA anomaly detection."""

    # 3D coordinates (first 3 PCs) for each row
    points_3d: list[list[float]]  # [[x,y,z], ...]
    # Per-row reconstruction error (MSE)
    reconstruction_errors: list[float]
    # 0 = normal, 1 = anomaly (by threshold)
    labels: list[int]
    # Row index in original CSV (0-based)
    row_indices: list[int]
    # Threshold used
    threshold: float
    # Feature names (for explainer)
    feature_names: list[str]
    # Explained variance ratio of first 3 components
    explained_variance_ratio: list[float]
    # Optional: ground truth if label column was provided
    ground_truth: list[int] | None
    # Number of components actually used (e.g. when auto-selected)
    n_components_used: int


def _choose_n_components_by_variance(
    X_fit: np.ndarray,
    variance_threshold: float = 0.95,
    min_components: int = 3,
) -> int:
    """Choose smallest k such that cumulative explained variance >= threshold (min 3 for 3D)."""
    n_features = X_fit.shape[1]
    n_samples = X_fit.shape[0]
    k_max = min(n_features, n_samples - 1, 20)
    if k_max < 1:
        return 1
    pca = PCA(n_components=k_max)
    pca.fit(X_fit)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    for k in range(1, len(cumvar) + 1):
        if cumvar[k - 1] >= variance_threshold:
            return max(min_components, k)
    return max(min_components, k_max)


def run_pca_anomaly(
    df: pd.DataFrame,
    feature_columns: list[str],
    label_column: str | None,
    n_components: int | None = 3,
    threshold_percentile: float = 95.0,
    variance_threshold_auto: float = 0.95,
) -> PCAAnomalyResult:
    """
    Run PCA on normal data (if labels exist) or all data; compute reconstruction
    error; label as anomaly if error > threshold (percentile of normal/all).
    """
    X = df[feature_columns].values
    n_rows = X.shape[0]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit PCA on normal only if we have labels, else on all data
    fit_mask = np.ones(n_rows, dtype=bool)  # all rows by default
    if label_column is not None and label_column in df.columns:
        y = df[label_column].values.ravel()
        y_binary = np.where(y == 0, 0, 1) if np.unique(y).size <= 2 else (y != y.min()).astype(int)
        normal_mask = y_binary == 0
        fit_mask = normal_mask
        X_fit = X_scaled[normal_mask]
        ground_truth = y_binary.tolist()
    else:
        X_fit = X_scaled
        ground_truth = None

    # Auto-select n_components by variance explained
    if n_components is None:
        n_components = _choose_n_components_by_variance(
            X_fit,
            variance_threshold=variance_threshold_auto,
            min_components=3,
        )
    n_components = min(n_components, X_fit.shape[1], X_fit.shape[0])
    pca = PCA(n_components=n_components)
    pca.fit(X_fit)
    n_components_used = n_components

    # Project all data and reconstruct
    X_proj = pca.transform(X_scaled)
    X_reconstructed = pca.inverse_transform(X_proj)
    reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)

    # Threshold: percentile of the distribution we fitted on (normal or all)
    thresh = np.percentile(reconstruction_error[fit_mask], threshold_percentile)

    labels = (reconstruction_error > thresh).astype(int).tolist()

    # 3D points: use first 3 components (pad with 0 if n_components was 1 or 2)
    points_3d = []
    for i in range(X_proj.shape[0]):
        row = X_proj[i].tolist()
        while len(row) < 3:
            row.append(0.0)
        points_3d.append(row[:3])

    explained = list(pca.explained_variance_ratio_)
    while len(explained) < 3:
        explained.append(0.0)

    return PCAAnomalyResult(
        points_3d=points_3d,
        reconstruction_errors=reconstruction_error.tolist(),
        labels=labels,
        row_indices=list(range(n_rows)),
        threshold=float(thresh),
        feature_names=feature_columns,
        explained_variance_ratio=explained[:3],
        ground_truth=ground_truth,
        n_components_used=n_components_used,
    )
