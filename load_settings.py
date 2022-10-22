import sys
from google.cloud import secretmanager

client_secret_manager = secretmanager.SecretManagerServiceClient()


def download(project_number, secret="tap_settings_files", location='settings.toml'):
    # Create GCP managed secret: https://console.cloud.google.com/security/secret-manager
    # Make sure to select upload file option, and upload your local copy of settings.toml
    name_medium_secret = "projects/{}/secrets/{}/versions/latest".format(project_number,secret)
    response = client_secret_manager.access_secret_version(name=name_medium_secret)
    pwd = response.payload.data.decode("UTF-8")
    with open(location, 'w') as outfile:
        outfile.write(pwd)


def upload(project_number, secret="tap_settings_files", file='settings.toml'):
    parent = client_secret_manager.secret_path(project_number, secret)
    with open(file, 'r') as outfile:
        payload = outfile.read().encode("UTF-8")
        response = client_secret_manager.add_secret_version(request={"parent": parent, "payload": {"data": payload}})
        if response.state == response.State.ENABLED:
            return '{} file was updated under GCP Secret Manager'.format(file)
        else:
            return 'May have been an issue updating {} file under GCP Secret Manager'.format(file)

#
# def create_secret(project_number, secret, file):
#     parent = client_secret_manager.secret_path(project_number, secret)
#
#     # Initialize request argument(s)
#     request = secretmanager.CreateSecretRequest(
#         parent= parent,
#         secret_id=secret,
#     )
#
#     # Make the request
#     response = client_secret_manager.create_secret(request=request)
#


if __name__ == "__main__":
    method = sys.argv[1]
    secret_name = sys.argv[2]
    project_number_input = sys.argv[3]
    download_location = sys.argv[4]
    if str(method) == 'download' and project_number_input:
        download(str(project_number_input), secret_name, download_location)
    elif str(method) == 'upload' and project_number_input:
        #project_number, secret="tap_settings_files", file='settings.toml'
        upload(str(project_number_input), secret_name, file)

