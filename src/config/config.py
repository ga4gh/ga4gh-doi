import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL",
                                      "postgresql+psycopg://user:password@localhost:5432/doi_db")

        self.doi_api_key = os.getenv("DOI_API_KEY", "")

        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

config = Config()
