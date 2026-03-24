#!/bin/bash
set -e

# Update these variables with your actual values if not already exported
export PROJECT_ID="${PROJECT_ID:-aimlexplore}"
export BUCKET_NAME="${BUCKET_NAME:-santytestdata26}"
export DATASTORE_ID="${DATASTORE_ID:-test_1774333509084}"
export COLLECTION_ID="${COLLECTION_ID:-default_collection}"
export LOCATION="${LOCATION:-us}" # Agent Engine / Discovery Engine Location
export SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-394260752043-compute@developer.gserviceaccount.com}"
export REGION="${REGION:-us-central1}" # Cloud Run Deployment Region
export TRIGGER_LOCATION="us" # Must explicitly match the GCS Bucket location (us multi-region)

# echo "Deploying Search Refresher to Cloud Run..."
# gcloud run deploy search-refresher \
#     --source . \
#     --set-env-vars="PROJECT_ID=${PROJECT_ID},DATASTORE_ID=${DATASTORE_ID},LOCATION=${LOCATION},COLLECTION_ID=${COLLECTION_ID}" \
#     --region=${REGION} \
#     --allow-unauthenticated

echo "Creating Eventarc trigger..."
gcloud eventarc triggers create gcs-to-search \
    --destination-run-service=search-refresher \
    --destination-run-region=${REGION} \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=${BUCKET_NAME}" \
    --service-account=${SERVICE_ACCOUNT} \
    --location=${TRIGGER_LOCATION}

print "Deployment complete."
