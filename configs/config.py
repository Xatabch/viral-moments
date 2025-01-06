import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API = os.getenv("OPENAI_API")
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME")
ARTICLE_SEARCH_QUERY = os.getenv("ARTICLE_SEARCH_QUERY")
DOWNLOADED_LINKS_FILE = os.getenv("DOWNLOADED_LINKS_FILE")
GPT_MODEL = os.getenv("GPT_MODEL")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEOS_FOLDER = os.getenv("VIDEOS_FOLDER")
ELEVEN_LABS_KEY = os.getenv("ELEVEN_LABS_KEY")
VOICE_FILE_NAME = os.getenv("VOICE_FILE_NAME")
OUTPUT_VIDEO_NAME = os.getenv("OUTPUT_VIDEO_NAME")
CONTENT_LANGUAGE = os.getenv("CONTENT_LANGUAGE")
TEXT_SIZE = int(os.getenv("TEXT_SIZE"))
TEXT_COLOR = os.getenv("TEXT_COLOR")
TEXT_FONT = os.getenv("TEXT_FONT")
VIDEO_WITH = int(os.getenv("VIDEO_WITH"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT"))
