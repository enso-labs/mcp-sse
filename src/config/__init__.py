import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Instructions(Enum):
    ENSO_CLOUD = (
        "You are a helpful Airtable assistant that can answer questions and help with tasks."
    )

class Config(Enum):
    APP_NAME = os.getenv("APP_NAME", 'Airtable MCP')
    APP_DEBUG = os.getenv("APP_DEBUG", True)
    APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", 'DEBUG')
    APP_PORT = os.getenv("APP_PORT", 8010)
    MCP_INSTRUCTIONS = os.getenv("MCP_INSTRUCTIONS", Instructions.ENSO_CLOUD.value)
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", 'this-is-a-test-key')