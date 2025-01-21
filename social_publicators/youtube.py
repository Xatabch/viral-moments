import os
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def authenticate_youtube_api(config):
    # Убедитесь, что у вас есть credentials.json, скачанный из Google Cloud Console
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    creds = None
    if os.path.exists(config["token_path"]):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(config["token_path"], SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config["credentials_path"], SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(config["token_path"], "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_file, title, description, config):
    youtube = authenticate_youtube_api(config)

    # Параметры загрузки
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [],
            "categoryId": "22",  # Категория: 22 = People & Blogs
            "shorts": True  # Указываем, что видео предназначено для Shorts
        },
        "status": {
            "privacyStatus": "public"  # Доступность видео: public, private, unlisted
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    id = response["id"]
    print("Video uploaded successfully!")
    print("Video URL: https://www.youtube.com/watch?v=" + id)

    return f"https://www.youtube.com/watch?v={id}"
