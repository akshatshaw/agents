from google.cloud import storage

# Your Google Cloud Project ID
project_id = "sage-archway-457103-s6"  # Replace with your actual project ID

# The name of your GCS bucket
bucket_name = "story_agent_audio"  # Replace with your actual bucket name

# The local file you want to upload
file_path = r"C:\Users\AKSHAT SHAW\OneDrive - iitr.ac.in\Desktop\Side-Projects\Agents\dubverse\app\64347083-9cb4-46ac-84ef-46010bb6ac24.mp3"  # Replace with the path to your local file

# The name you want to give the file in GCS
destination_blob_name = "uploaded_file.mp3"
import os
from dotenv import load_dotenv
load_dotenv()

api_key_string =os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") 
def upload_file_to_gcs(bucket_name, file_path, destination_blob_name):
    """Uploads a file to the Google Cloud Storage bucket."""
    try:
        storage_client = storage.Client(project=project_id, credentials= None, client_options={"api_key": api_key_string})
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blobs = bucket.list_blobs()
        print("Blobs in the bucket:")
        for blob in blobs:
            print(f"- {blob.name}")
        # blob.upload_from_filename(file_path)

        # print(f"File {file_path} uploaded to {destination_blob_name} in bucket {bucket_name}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    upload_file_to_gcs(bucket_name, file_path, destination_blob_name)
    
# from google.cloud import resourcemanager_v3
# from google.iam.v1 import iam_policy_pb2, policy_pb2


# def get_project_policy(project_id: str) -> policy_pb2.Policy:
#     """Get policy for project.

#     project_id: ID or number of the Google Cloud project you want to use.
#     """

#     client = resourcemanager_v3.ProjectsClient()
#     request = iam_policy_pb2.GetIamPolicyRequest()
#     request.resource = f"projects/{project_id}"

#     policy = client.get_iam_policy(request)
#     print(f"Policy retrieved: {policy}")

#     return policy