import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "smart_wardrobe")
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

ITEM_MODEL_PATH = os.getenv("ITEM_MODEL_PATH", "./item_classifier_resnet50.pt")
ATTRIBUTE_MODEL_PATH = os.getenv("ATTRIBUTE_MODEL_PATH", "./attribute_classifier_resnet50.pt")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")