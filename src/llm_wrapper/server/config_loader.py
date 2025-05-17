# src/server/config_loader.py

import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, ValidationError
from llm_wrapper.lib.logging import setup_logger

logger = setup_logger("llm-server", "logs/server.log")

CONFIG_DIR = Path(__file__).parent.parent / "configs"

class ApiConfig(BaseModel):
    url: str

class ModelPath(BaseModel):
    path: str

class Parameters(BaseModel):
    temperature: float = 0.7
    top_p: float = 1.0
    top_k: int = 40
    stream: bool = False

class ModelConfig(BaseModel):
    api: ApiConfig
    model: ModelPath
    system_prompt: str = Field(default="")
    parameters: Parameters = Field(default_factory=Parameters)
    model_id: str

def load_all_configs() -> dict:
    """
    Load all YAML model configuration files from the configs directory.

    Returns:
        dict: A dictionary mapping model_id to its loaded configuration.
    """
    # Resolve config directory path (support str or Path)
    config_dir = Path(CONFIG_DIR)
    logger.debug(f"Attempting to load configs from directory: {config_dir}")
    configs = {}

    if not config_dir.exists():
        logger.warning(f"Config directory not found: {config_dir}")
        return configs

    for file_path in config_dir.iterdir():
        if not file_path.name.endswith((".yaml", ".yml")):
            continue
        model_id = file_path.stem
        try:
            data = yaml.safe_load(file_path.read_text()) or {}
            data["model_id"] = model_id
            # Validate schema
            cfg = ModelConfig(**data)
            configs[model_id] = cfg.model_dump()
            logger.info(f"Loaded config for model '{model_id}' from '{file_path.name}'")
        except ValidationError as ve:
            logger.error(f"Configuration validation error in '{file_path.name}': {ve}")
        except Exception as e:
            logger.exception(f"Failed to load config file '{file_path.name}': {e}")

    logger.debug(f"Total configs loaded: {len(configs)}")
    return configs
 
# Load all configs at import for reuse
CONFIGS = load_all_configs()