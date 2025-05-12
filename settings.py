from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
    FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")
    MONGO_URI = os.getenv("MONGO_URI")
