import io
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    AnomalyRowDetail,
    RunRequest,
    RunResponse,
    TopFeature,
    UploadResponse,
)
from app.config import settings
from app.services import (
    get_feature_contributions,
    load_and_validate_csv,
    run_pca_anomaly,
)

router = APIRouter(prefix="/api", tags=["pca-anomaly"])

# In-memory store (Catatan: Ini akan terhapus jika Render melakukan restart/spin down)
_current_df = None
_current_feature_columns: list[str] = []
_current_label_column: str | None = None
_current_labels: list[int] | None = None 


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    label_column: str | None = Form(None),
    encoding: str = Form("utf-8"),
):
    global _current_df, _current_feature_columns, _current_label_column

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size_mb} MB.",
        )

    result = load_and_validate_csv(
        content,
        file.filename or "upload.csv",
        label_column=label_column,
        encoding=encoding,
    )

    if result.error:
        return UploadResponse(
            success=False,
            error=result.error,
            n_rows=result.n_rows,
            n_features=result.n_features,
            feature_columns=result.feature_columns,
            label_column=result.label_column,
        )

    _current_df = result.df
    _current_feature_columns = result.feature_columns
    _current_label_column = result.label_column
    _current_labels = None 

    return UploadResponse(
        success=True,
        n_rows=result.n_rows,
        n_features=result.n_features,
        feature_columns=result.feature_columns,
        label_column=result.label_column,
    )

@router.post("/run", response_model=RunResponse)
async def run_anomaly_detection(body: RunRequest | None = None):
    global _current_df, _current_feature_columns, _current_label_column, _current_labels

    if _current_df is None or not _current_feature_columns:
        raise HTTPException(
            status_code=400,
            detail="Upload a CSV first via POST /api/upload.",
        )

    opts = body or RunRequest()
    n_components_arg = opts.n_components 
    if n_components_arg is not None:
        n_components_arg = min(
            n_components_arg,
            len(_current_feature_columns),
            len(_current_df),
        )

    result = run_pca_anomaly(
        df=_current_df,
        feature_columns=_current_feature_columns,
        label_column=_current_label_column,
        n_components=n_components_arg,
        threshold_percentile=opts.threshold_percentile,
    )
    n_components_used = result.n_components_used

    details = get_feature_contributions(
        df=_current_df,
        feature_columns=_current_feature_columns,
        label_column=_current_label_column,
        n_components=n_components_used,
        threshold_percentile=opts.threshold_percentile,
        top_k=5,
    )

    anomaly_details = [
        AnomalyRowDetail(
            row_index=d["row_index"],
            is_anomaly=d["is_anomaly"],
            reconstruction_error=d["reconstruction_error"],
            top_features=[TopFeature(name=t["name"], contribution=t["contribution"]) for t in d["top_features"]],
        )
        for d in details
    ]

    _current_labels = result.labels

    return RunResponse(
        points_3d=result.points_3d,
        reconstruction_errors=result.reconstruction_errors,
        labels=result.labels,
        row_indices=result.row_indices,
        threshold=result.threshold,
        feature_names=result.feature_names,
        explained_variance_ratio=result.explained_variance_ratio,
        ground_truth=result.ground_truth,
        n_components_used=n_components_used,
        anomaly_details=anomaly_details,
    )

@router.get("/download/cleaned")
async def download_cleaned_csv():
    global _current_df, _current_labels
    if _current_df is None or _current_labels is None:
        raise HTTPException(status_code=400, detail="Upload a CSV and run PCA first.")
    
    mask = [l == 0 for l in _current_labels]
    cleaned = _current_df.loc[mask]
    buf = io.StringIO()
    cleaned.to_csv(buf, index=False)
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cleaned_normal_only.csv"},
    )

@router.get("/download/anomalies")
async def download_anomalies_csv():
    global _current_df, _current_labels
    if _current_df is None or _current_labels is None:
        raise HTTPException(status_code=400, detail="Upload a CSV and run PCA first.")
    
    mask = [l == 1 for l in _current_labels]
    anomalies = _current_df.loc[mask]
    buf = io.StringIO()
    anomalies.to_csv(buf, index=False)
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=anomalies_only.csv"},
    )