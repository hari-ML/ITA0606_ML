# Enables required Google Cloud APIs for remote build and Cloud Run deployment
Write-Host "Enabling Cloud Run, Cloud Build, and Artifact Registry APIs..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to enable Google Cloud services. Verify gcloud auth and project configuration."
    exit $LASTEXITCODE
}
Write-Host "Required Google Cloud APIs enabled successfully." -ForegroundColor Green
