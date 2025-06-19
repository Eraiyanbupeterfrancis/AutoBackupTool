import os
import io
import zipfile
from cryptography.fernet import Fernet
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("backup.env")

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")

def get_drive_instance():
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(CLIENT_SECRETS_FILE)
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile("mycreds.txt")
    else:
        gauth.Authorize()
    return GoogleDrive(gauth)

def compress_and_encrypt_folder(folder_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.join(folder_path, '..'))
                zipf.write(file_path, arcname)
    buf.seek(0)
    fernet = Fernet(ENCRYPTION_KEY.encode())
    encrypted = fernet.encrypt(buf.read())
    return io.BytesIO(encrypted)

def upload_to_drive_stream(encrypted_stream, filename):
    drive = get_drive_instance()
    file_drive = drive.CreateFile({'title': filename})
    encrypted_stream.seek(0)
    file_drive.SetContentString(encrypted_stream.read().decode('latin1'))
    file_drive.Upload()

    # Enforce 5 backup limit
    file_list = drive.ListFile({'q': f"title contains 'backup_'"}).GetList()
    if len(file_list) > 5:
        # Delete oldest
        file_list.sort(key=lambda f: f['createdDate'])
        file_list[0].Delete()

    return file_drive['alternateLink']

def log_backup(filename, link):
    log_file = 'backup_log.json'
    log = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                content = f.read().strip()
                if content:
                    log = json.loads(content)
        except json.JSONDecodeError:
            log = []
    log.append({
        'file': filename,
        'timestamp': datetime.now().isoformat(),
        'cloud_link': link
    })
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)

def list_backups():
    drive = get_drive_instance()
    files = drive.ListFile({'q': f"title contains 'backup_'"}).GetList()
    return [(f['title'], f['id']) for f in files]

def restore_backup(file_id, dest_folder, progress_callback=None):
    drive = get_drive_instance()
    file_drive = drive.CreateFile({'id': file_id})

    # Download encrypted content
    file_drive.FetchMetadata()
    content = file_drive.GetContentString().encode('latin1')
    if progress_callback:
        progress_callback(50)

    # Decrypt and extract
    decrypt_and_extract(content, dest_folder)
    if progress_callback:
        progress_callback(100)

def decrypt_and_extract(encrypted_bytes, dest_folder):
    fernet = Fernet(ENCRYPTION_KEY.encode())
    decrypted = fernet.decrypt(encrypted_bytes)
    buf = io.BytesIO(decrypted)
    with zipfile.ZipFile(buf, 'r') as zipf:
        zipf.extractall(dest_folder)
