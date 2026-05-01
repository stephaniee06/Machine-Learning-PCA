# PCA Anomaly Demo

Web app to upload a CSV, run PCA-based anomaly detection, view a 3D scatter of the first three principal components (normal vs anomaly), and see which rows are anomalies and which features contribute most.

## Stack

- **Backend:** FastAPI
- **Frontend:** React (Vite), HTML, CSS, JS, Three.js for 3D visualization

## Project structure

```
Prototype/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── api/
│   │   │   ├── routes.py     # POST /api/upload, POST /api/run
│   │   │   └── schemas.py    # Pydantic models
│   │   └── services/
│   │       ├── data_loader.py   # CSV load & validate
│   │       ├── pca_anomaly.py   # PCA fit, reconstruction error, threshold
│   │       └── explainer.py     # Per-row feature contributions
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── RunControls.jsx
│   │   │   ├── Scatter3D.jsx    # Three.js 3D scatter
│   │   │   └── AnomalyTable.jsx
│   │   └── api/client.js
│   ├── index.html
│   └── package.json
└── README.md
```

## Run the app (2 terminals)

You will run **two dev servers** at the same time:

- **Terminal 1 (Backend)**: FastAPI on `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
- **Terminal 2 (Frontend)**: Vite on `http://localhost:5173`

Pick the instructions for your OS below.

---

## Run on Windows (PowerShell)

### Terminal 1 — Backend

```powershell
cd "C:\Users\Alif Akbar Hafiz\Desktop\Perbinusan\4th Semester\A_MachineLearning\FinalProjectProposal\Prototype\backend"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend

```powershell
cd "C:\Users\Alif Akbar Hafiz\Desktop\Perbinusan\4th Semester\A_MachineLearning\FinalProjectProposal\Prototype\frontend"
npm install
npm run dev
```

### Common Windows notes

- If venv activation is blocked in PowerShell, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- If `pip install -r requirements.txt` fails building `numpy/pandas`, install **64-bit Python** (Python 3.11/3.12 recommended), delete `.venv`, then repeat the backend steps.

---

## Run on macOS / Linux (Terminal)

### Terminal 1 — Backend

```bash
cd "/path/to/Prototype/backend"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend

```bash
cd "/path/to/Prototype/frontend"
npm install
npm run dev
```

If `python3 -m venv` fails on Linux, install venv support:

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y python3-venv python3-pip
```

---

## Run on WSL (Windows Subsystem for Linux)

### Terminal 1 (WSL) — Backend

```bash
cd /mnt/c/Users/Alif\ Akbar\ Hafiz/Desktop/Perbinusan/4th\ Semester/A_MachineLearning/FinalProjectProposal/Prototype/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 (WSL) — Frontend

```bash
cd /mnt/c/Users/Alif\ Akbar\ Hafiz/Desktop/Perbinusan/4th\ Semester/A_MachineLearning/FinalProjectProposal/Prototype/frontend
npm install
npm run dev
```

### WSL note (important)

- If your distro is **WSL 1**, some Node installations (especially `nvm`) may refuse to run and show: “WSL 1 is not supported…”. The recommended fix is upgrading the distro to **WSL 2**:
  - PowerShell: `wsl -l -v` (copy the distro name)
  - PowerShell (Admin): `wsl --set-version <DistroName> 2`

---

## Run locally (other environments)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # WSL / Linux / macOS
# .venv\Scripts\activate    # Windows PowerShell/cmd
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dev server proxies `/api` to the backend.

### Without proxy

If you run the frontend on another port or host, set the backend URL in the frontend (e.g. in `src/api/client.js` use `http://127.0.0.1:8000/api` as base) and ensure CORS allows that origin in `backend/app/config.py`.

## Usage

1. **Upload CSV** – Choose a CSV with numeric columns. Optionally specify a label column (0 = normal, 1 = anomaly); if provided, PCA is fitted on normal rows only.
2. **Run** – Set number of components and threshold percentile, then click Run.
3. **3D view** – Green = normal, red = anomaly in the space of the first three principal components. Drag to rotate, scroll to zoom.
4. **Anomaly table** – Lists anomaly rows (or all rows via “Show all”), row index, reconstruction error, and top contributing features.

## API

- **POST /api/upload** – `multipart/form-data`: `file` (CSV), optional `label_column`, `encoding`. Returns `n_rows`, `n_features`, `feature_columns`, `label_column`.
- **POST /api/run** – JSON body: `n_components`, `threshold_percentile`. Returns `points_3d`, `labels`, `reconstruction_errors`, `anomaly_details` (row index, error, top features), etc.

API docs: [http://localhost:8000/docs](http://localhost:8000/docs).
