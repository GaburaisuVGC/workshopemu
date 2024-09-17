import os
import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth
import mimetypes
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Load environment variables from .env file
load_dotenv()

# Define the environment variables
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = 'localhost:9099'
os.environ['FIREBASE_STORAGE_EMULATOR_HOST'] = 'localhost:9199'
os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'

# Get the environment variables
service_account_path = os.getenv("SERVICE_ACCOUNT")
project_id = os.getenv("PROJECT_ID")
bucket_name = os.getenv("BUCKET_NAME", 'default-bucket')  # 'default-bucket' if not provided

# Initialize Firebase with the service account and project ID
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'projectId': project_id,
    'storageBucket': bucket_name
})

# Initialize Firestore
db = firestore.client()

# Define the folder path where the files are stored
folder_path = 'files'

# Create a user using the Firebase Admin SDK
def create_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        print(f'Utilisateur {user.uid} créé avec succès.')
        return user
    except Exception as e:
        print(f'Erreur lors de la création de l\'utilisateur: {e}')
        return None

# Authenticate the user using the Firebase Auth REST API
def authenticate_user(email, password):
    auth_url = f'http://{os.environ["FIREBASE_AUTH_EMULATOR_HOST"]}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=any'

    payload = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }

    response = requests.post(auth_url, json=payload)

    if response.status_code == 200:
        id_token = response.json()['idToken']
        print('Authentification réussie.')
        return id_token
    else:
        print('Échec de l\'authentification.')
        print(response.json())
        return None

# Upload a file to the Firebase Storage bucket
def upload_file_to_bucket(file_path, file_name, id_token):
    storage_url = f'http://{os.environ["FIREBASE_STORAGE_EMULATOR_HOST"]}/upload/storage/v1/b/{bucket_name}/o'

    # Determine the content type of the file
    content_type, encoding = mimetypes.guess_type(file_name)
    if content_type is None:
        content_type = 'application/octet-stream'

    headers = {
        'Authorization': f'Bearer {id_token}',
    }

    params = {
        'uploadType': 'multipart',
        'name': file_name
    }

    metadata = {
        'name': file_name,
        'contentType': content_type
    }

    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Generate a unique boundary
    boundary = 'my_boundary'

    # Create the multipart body
    multipart_body = (
        f'--{boundary}\r\n'
        'Content-Type: application/json; charset=UTF-8\r\n\r\n'
        f'{json.dumps(metadata)}\r\n'
        f'--{boundary}\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    # Define the headers
    headers['Content-Type'] = f'multipart/related; boundary={boundary}'

    response = requests.post(
        storage_url,
        headers=headers,
        params=params,
        data=multipart_body
    )

    if response.status_code == 200:
        print(f'Fichier {file_name} uploadé dans le bucket.')
        return True
    else:
        print(f'Échec de l\'upload du fichier {file_name}.')
        print(response.json())
        return False
    
# Log the file event in Firestore
def log_file_event(file_name, event):
    doc_ref = db.collection('file_logs').document()
    doc_ref.set({
        'file_name': file_name,
        'event': event,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    print(f'Log créé pour le fichier : {file_name}')

# Main
if __name__ == '__main__':
    # User credentials
    user_email = 'user@example.com'
    user_password = 'password123'

    # Create the user
    user = create_user(user_email, user_password)

    if user:
        # Authenticate the user
        id_token = authenticate_user(user_email, user_password)

        if id_token:
            # Check if the folder exists
            if os.path.isdir(folder_path):
                # List the files in the folder
                files = os.listdir(folder_path)

                if files:
                    for file_name in files:
                        file_path = os.path.join(folder_path, file_name)

                        # Verify if the file exists and is a file (not a directory)
                        if os.path.isfile(file_path):
                            # Upload the file to the bucket
                            if upload_file_to_bucket(file_path, file_name, id_token):
                                # Log the file event in Firestore
                                log_file_event(file_name, 'uploaded')
                            else:
                                print(f'Échec de l\'upload du fichier {file_name}.')
                        else:
                            print(f'{file_name} n\'est pas un fichier, il sera ignoré.')
                else:
                    print(f'Aucun fichier trouvé dans le dossier {folder_path}.')
            else:
                print(f'Le dossier {folder_path} n\'existe pas.')
        else:
            print('Impossible d\'authentifier l\'utilisateur. Opération annulée.')
    else:
        print('Impossible de créer l\'utilisateur. Opération annulée.')
