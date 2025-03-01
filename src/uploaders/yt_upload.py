import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/config/client_secret_222696419024-61veioon47jeaud9lung9e5e12bnf1lc.apps.googleusercontent.com.json"
TOKEN_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/config/token.json"

CATEGORY_TO_ID_MAPPING = {
    "Aviation": 28
}
DESCRIPTIONS = {
    "Aviation": "What to know more about aviation? Follow us. #Shorts"
}


def authenticate_youtube():
    credentials = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as token_file:
            credentials_data = json.load(token_file)
            credentials = Credentials.from_authorized_user_info(credentials_data, SCOPES)

    if not credentials or not credentials.refresh_token:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_PATH,
            SCOPES
        )
        credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(credentials.to_json())

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return build("youtube", "v3", credentials=credentials)


def upload_shorts(youtube, video_file, title, tags, topic, status="private", output_dir="videos_data.txt"):
    if "#Shorts" not in title:
        title += " #Shorts"

    description = DESCRIPTIONS[topic]

    with open(output_dir, "w") as f:
        f.write(title)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": CATEGORY_TO_ID_MAPPING.get(topic, "22"),
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": status,
                "madeForKids": False,
            },
        },
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print("Upload Complete!")
    print("Video ID:", response["id"])
    return response["id"]

if __name__ == "__main__":
    upload_shorts(
        authenticate_youtube(),
        "/Users/wnowogorski/PycharmProjects/TikTokGenerator/generated_videos/video_0.mp4",
        title="Test video #Shorts",
        tags=["test"],
        topic="Aviation",
    )
