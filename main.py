import os
from google.cloud import discoveryengine_v1 as discoveryengine
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["POST"])
def gcs_trigger():
    # 1. Parse the Eventarc event to get the file path
    event_data = request.get_json()
    if not event_data or 'bucket' not in event_data or 'name' not in event_data:
        return "Invalid event data", 400
        
    bucket = event_data['bucket']
    name = event_data['name']
    gcs_uri = f"gs://{bucket}/{name}"

    # 2. Tell Vertex AI Search to ingest this specific file
    try:
        client = discoveryengine.DocumentServiceClient()
        project_id = os.getenv('PROJECT_ID')
        datastore_id = os.getenv('DATASTORE_ID')
        location = os.getenv('LOCATION', 'global')
        collection_id = os.getenv('COLLECTION_ID', 'default_collection')
        
        if not project_id or not datastore_id:
            return "Missing PROJECT_ID or DATASTORE_ID environment variables", 500
            
        parent = f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{datastore_id}/branches/0"
        
        request_body = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=discoveryengine.GcsSource(input_uris=[gcs_uri]),
        )
        
        # Initiate the import request
        client.import_documents(request=request_body)
        return f"Indexing started for {gcs_uri}", 200
        
    except Exception as e:
        print(f"Error starting index job: {e}")
        return f"Error: {e}", 500

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, falling back to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
