// Menggunakan API lokal jika dijalankan di localhost, atau API Render jika di production
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? '/api'
  : 'https://machine-learning-pca-backend.onrender.com/api';

/**
 * Upload CSV file to the backend on Render.
 */
export async function uploadCsv(file, labelColumn = null, encoding = 'utf-8') {
  const form = new FormData();
  form.append('file', file);
  if (labelColumn) form.append('label_column', labelColumn);
  form.append('encoding', encoding);

  // Sekarang fetch akan menembak ke: https://machine-learning-pca-backend.onrender.com/api/upload
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: form,
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

/**
 * Run PCA anomaly detection.
 */
export async function runAnomalyDetection(options = {}) {
  const { n_components = 3, threshold_percentile = 95 } = options;
  const body = {
    threshold_percentile: Number(threshold_percentile),
  };
  
  if (n_components === 'auto' || n_components === null || n_components === undefined) {
    body.n_components = null;
  } else {
    body.n_components = Number(n_components);
  }

  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Run failed');
  }
  return res.json();
}

/**
 * Download CSV of the dataset with anomaly rows removed (normal rows only).
 */
export async function downloadCleanedCsv() {
  const res = await fetch(`${API_BASE}/download/cleaned`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Download failed');
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cleaned_normal_only.csv';
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Download CSV containing only the rows classified as anomalies.
 */
export async function downloadAnomaliesCsv() {
  const res = await fetch(`${API_BASE}/download/anomalies`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Download failed');
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'anomalies_only.csv';
  a.click();
  URL.revokeObjectURL(url);
}