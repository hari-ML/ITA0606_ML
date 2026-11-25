# Google Cloud Run Deployment Guide

Deploy **"Android Malware Detection Using Permission and API-Call Features with SVM"** remotely via Google Cloud Build and Google Cloud Run—without installing or running Docker locally on Windows.

---

## Step-by-Step Deployment

1. **Install Google Cloud CLI (`gcloud`) on Windows**
   Download and run the official installer: https://cloud.google.com/sdk/docs/install-sdk#windows

2. **Authenticate Your Google Account**
   ```powershell
   gcloud auth login
   ```

3. **Select Your Google Cloud Project**
   Replace `<PROJECT_ID>` with your GCP Project ID:
   ```powershell
   gcloud config set project <PROJECT_ID>
   ```

4. **Set a Billing Budget Alert (Recommended)**
   In Google Cloud Console -> **Billing -> Budgets & alerts -> Create Budget** (e.g., set a low alert threshold such as $5 / INR 500 with email alerts at 50%, 90%, and 100%).

5. **Enable Required Google Cloud APIs**
   Run the setup script once:
   ```powershell
   .\setup_gcloud.ps1
   ```
   *(Runs `gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com`)*

6. **Build Remotely & Deploy to Cloud Run**
   Run the deploy script:
   ```powershell
   .\deploy.ps1
   ```
   *(Runs `gcloud run deploy malware-detector --source . --region asia-south1 --allow-unauthenticated --memory 2Gi --cpu 1 --timeout 300 --max-instances 2 --min-instances 0`)*

7. **Open the Service URL**
   Once Cloud Build finishes, copy the `Service URL` (`https://malware-detector-....a.run.app`) printed in PowerShell and open it in your browser.

---

## Container Notes

- **No Local Docker Needed**: `gcloud run deploy --source .` zips only the files allowed by `.gcloudignore` (including `app.py`, `styles.py`, `src/`, `model/`, `assets/`, `.streamlit/`, and `requirements.txt`) and builds the image remotely on Cloud Build.
- **Python 3.12 Alignment**: `Dockerfile` uses `python:3.12-slim` because the pinned `numpy==2.5.5` and `scipy==1.18.1` packages matching your local environment require Python `>=3.12` on PyPI.
- **Upload Size Limit**: Cloud Run enforces a 32 MB HTTP request limit; both `.streamlit/config.toml` and `app.py` enforce a **30 MB** maximum APK upload size.

---

## Troubleshooting

| Symptom | Cause | Fix |
|:---|:---|:---|
| **Container failed to start / PORT binding error** | Streamlit did not bind `0.0.0.0` on `$PORT`. | Confirm `Dockerfile` runs `sh -c "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 ..."` and `app.py` does not crash at import time. Check **Cloud Run -> Logs** in GCP Console. |
| **Container Out-of-Memory (OOM / HTTP 503)** | Large APKs with multiple DEX files or F-Droid index parsing exceed 2 GiB RAM (Cloud Run `/tmp` shares container RAM). | Edit `deploy.ps1` and increase `--memory 2Gi` to `--memory 4Gi`, then re-run `.\deploy.ps1`. |
| **`scikit-learn` / `numpy` version mismatch or pickle error** | Model `.pkl` files were serialized with `scikit-learn==1.9.1` and `numpy==2.5.5` under Python 3.12. | Keep exact versions pinned in `requirements.txt` and `FROM python:3.12-slim` in `Dockerfile`. |
| **HTTP 403 / 413 on File Upload** | Uploaded APK exceeds Cloud Run's 32 MB request limit, or Streamlit XSRF/CORS blocks proxied requests. | Ensure the uploaded `.apk` is under **30 MB**, and keep `--server.enableCORS=false --server.enableXsrfProtection=false` in `Dockerfile`. |
