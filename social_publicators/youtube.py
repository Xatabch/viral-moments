import os
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def authenticate_youtube_api():
    # Убедитесь, что у вас есть credentials.json, скачанный из Google Cloud Console
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    creds = None
    if os.path.exists("token.json"):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_file, title, description):
    youtube = authenticate_youtube_api()

    # Параметры загрузки
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["Python", "YouTube API", "Shorts"],
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

    print("Video uploaded successfully!")
    print("Video URL: https://www.youtube.com/watch?v=" + response["id"])

if __name__ == "__main__":
    upload_video_to_youtube('output.mp4', 'Tech news #TikTok#TechNews#AI#History#TechUpdate', "Catch up on the latest tech updates! TikTok returns in the US after a temporary ban, with a potential joint venture on the horizon. Plus, AI's struggle with history questions reveals its limitations. Don't miss out on these trending stories.")
