# Deploys the Streamlit Android Malware Detection app to Google Cloud Run (remote build via Cloud Build)
Write-Host "Deploying malware-detector to Google Cloud Run (asia-south1)..." -ForegroundColor Cyan
gcloud run deploy malware-detector --source . --region asia-south1 --allow-unauthenticated --memory 2Gi --cpu 1 --timeout 300 --max-instances 2 --min-instances 0
if ($LASTEXITCODE -ne 0) {
    Write-Error "Cloud Run deployment failed. Check Cloud Build logs in Google Cloud Console."
    exit $LASTEXITCODE
}
Write-Host "Deployment complete. Open the Service URL printed above." -ForegroundColor Green
