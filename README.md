# tesla-control

# Summary
Wrapped [TeslaPy](https://github.com/tdorssers/TeslaPy) python module into a GCP Cloud Function that allow you to
- Lock/Unlock
- Set temp

Currently, this service is using GCP as compute, but the core logic can live anywhere.

# Setup For GCP
- Set up GCP project, and IAM service accounts
- Tesla Credential: Find out how to generate cache.json Tesla credential file [here](https://github.com/tdorssers/TeslaPy)
- Set up Jobs in GCP Scheduler 


# Optional
- [Secret Manager](gcp/secret_manager.py): You can choose to store your cache.json file in GCP Secret manager or store it locally. You can use secret_manager.py script to assist with this.
- [Cloud Build](gcp/cloudbuild.yaml): can use [cloudbuild.yaml](gcp/cloudbuild.yaml) to build out the Cloud Function.
