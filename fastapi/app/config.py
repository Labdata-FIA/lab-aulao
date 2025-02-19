import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE: str = os.getenv("DATABASE")
    COLLECTION_PRODUCT: str = os.getenv("COLLECTION_PRODUCT")

settings = Settings()