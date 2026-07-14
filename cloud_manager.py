import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
from system_config import GDRIVE_CREDENTIALS, GDRIVE_FOLDER_ID
from utils.logger import logger

class GoogleDriveHandler:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""

        logger.info(
            "Authenticating with Google Drive."
        )

        try:
            TOKEN_FILE = "token.pickle"

            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    self.creds = pickle.load(token)
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(GDRIVE_CREDENTIALS):
                        raise FileNotFoundError(
                            f"Credentials file not found: {GDRIVE_CREDENTIALS}"
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GDRIVE_CREDENTIALS, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            self.service = build('drive', 'v3', credentials=self.creds)

            logger.info(
                "Google Drive authentication successful."
            )

        except Exception:
            logger.exception(
                "Failed to authenticate with Google Drive API."
            )
            raise
    
    def upload_file(
        self,
        file_path: str,
        file_name: str,
        mime_type: str,
        folder_id: str | None = None
    ) -> str:
        """
        Upload a local file to the configured
        Google Drive folder.

        Returns
        -------
        str
            Uploaded file ID.
        """

        logger.info(
            "Uploading %s to Google Drive.",
            file_name
        )

        try:
            folder_id = folder_id or GDRIVE_FOLDER_ID

            if not folder_id:
                raise ValueError(
                    "Google Drive folder ID is not configured."
                )
        
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type)

            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"File not found: {file_path}"
                )
            
            try:
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            except Exception:
                logger.exception(
                    "Google Drive upload failed."
                )
                raise

            logger.info(
                "Successfully uploaded %s.",
                file_name
            )
            
            return file.get('id')
        
        except Exception:
            logger.exception(
                "Failed to upload %s to Google Drive.",
                file_name
            )
            raise
    
    def download_file(
        self, 
        file_id: str, 
        destination_path: str
    ):
        """
        Download a file from Google Drive.

        Returns
        -------
        None
        """
        logger.info(
            "Downloading file %s.",
            file_id
        )

        try:
            request = self.service.files().get_media(fileId=file_id)
            with open(destination_path, 'wb') as f:
                f.write(request.execute())

                logger.info(
                    "Retrieved %d files from Google Drive.",
                    len(file_id)
                )
        except Exception:
            logger.exception(
                "Failed to download file %s from Google Drive.",
                file_id
            )
            raise

    def list_files(
        self, 
        folder_id: str | None = None
    ):
        """List files in Google Drive folder"""

        try:
            folder_id = folder_id or GDRIVE_FOLDER_ID

            if not folder_id:
                raise ValueError(
                    "Google Drive folder ID is not configured."
                )
            
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, createdTime)"
            ).execute()
            
            return results.get('files', [])
        
        except Exception:
            logger.exception(
                "Failed to list files in folder %s.",
                folder_id
            )
            raise