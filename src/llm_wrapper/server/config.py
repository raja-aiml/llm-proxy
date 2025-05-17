# src/server/config.py

import os
from dotenv import load_dotenv
from llm_wrapper.lib.logging import setup_logger

# Initialize environment variables
load_dotenv()

# Set up logger
logger = setup_logger("llm-server", "logs/server.log")
logger.debug("Loading configuration from environment variables.")


# Request timeout settings
DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TIMEOUT", "60"))
STREAMING_TIMEOUT = int(os.environ.get("STREAMING_TIMEOUT", "300"))

# Server runtime configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# Log loaded settings for debugging (only safe values)
logger.debug("Config loaded: HOST=%s, PORT=%s, DEFAULT_TIMEOUT=%s, STREAMING_TIMEOUT=%s", 
             HOST, PORT, DEFAULT_TIMEOUT, STREAMING_TIMEOUT)
