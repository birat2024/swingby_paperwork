from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging

def upload_to_drive(file_stream, file_name, folder_id):
    try:
        gauth = GoogleAuth()
        
        # Try to load saved credentials
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        gauth.SaveCredentialsFile("mycreds.txt")

        drive = GoogleDrive(gauth)

        # Create a file on Google Drive
        file_metadata = {'title': file_name, 'parents': [{'id': folder_id}]}
        file_drive = drive.CreateFile(file_metadata)

        # Read file data from the stream
        file_drive.content = file_stream

        # Upload the file
        file_drive.Upload()
        return file_drive['id']
    except Exception as e:
        logging.exception("Error uploading file to Google Drive")
        raise e
