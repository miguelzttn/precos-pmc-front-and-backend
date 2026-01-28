import os
from dotenv import load_dotenv

# For Windows compatibility
load_dotenv()


class Config:
    """Configuration class to manage environment variables."""

    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "chave_secreta_padrao")


settings = Config()
