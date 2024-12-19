from googleapiclient.http import MediaIoBaseUpload
import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials() -> Credentials:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_folder(folder_name: str) -> str | None:
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        print(f"Folder '{folder_name}' created with ID: {folder.get('id')}")
        return folder.get('id')
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def create_text_file_in_folder(file_name: str, content: str, folder_id: str) -> None:
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        file_stream = io.BytesIO(content.encode('utf-8'))
        media = MediaIoBaseUpload(file_stream, mimetype='text/plain')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File '{file_name}' created with ID: {file.get('id')}")
    except HttpError as error:
        print(f'An error occurred: {error}')

def list_folders() -> None:
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        folders = results.get('files', [])
        if not folders:
            print('No folders found.')
        else:
            print('Folders:')
            for folder in folders:
                print(f"Name: {folder['name']}, ID: {folder['id']}")
    except HttpError as error:
        print(f'An error occurred: {error}')

def list_files_by_name() -> None:
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        query = "trashed=false"
        results = service.files().list(
            q=query,
            orderBy="name",
            fields="nextPageToken, files(id, name)"
        ).execute()
        files = results.get('files', [])
        if not files:
            print('No files found.')
        else:
            print('Files:')
            for file in files:
                print(f"Name: {file['name']}, ID: {file['id']}")
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    folder_id = create_folder('api_test2')
    if folder_id:
        create_text_file_in_folder('example.txt', 'Hello, World!', folder_id)
    list_folders()
    list_files_by_name()
