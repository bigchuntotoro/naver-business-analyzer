import os
from dotenv import load_dotenv

load_dotenv()


NAVER_CLIENT_ID = os.getenv(
    "NAVER_CLIENT_ID"
)

NAVER_CLIENT_SECRET = os.getenv(
    "NAVER_CLIENT_SECRET"
)


PUBLIC_DATA_KEY = os.getenv(
    "PUBLIC_DATA_KEY"
)


OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)