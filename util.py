"""
Utility functions for SKU processing and GPU memory management.
"""
import gc
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Log to a file with rotation and retention policies
if not os.path.exists("logs"):
    os.makedirs("logs")

# Now this works
logger.add(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log", rotation="500MB", retention="1 week")


def get_sku_brief() -> Dict[str, Any]:
    """
    Load SKU brief data from JSON file.

    Returns:
        dict: SKU brief data loaded from JSON file.

    Raises:
        FileNotFoundError: If the sku_brief.json file is not found.
        json.JSONDecodeError: If the JSON file contains invalid syntax.
    """
    try:
        file_path = Path("./input/sku_brief.json")
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("SKU brief file not found at path: %s", file_path.absolute())
        raise
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in sku_brief.json: %s", str(e))
        raise


def clear_cuda_cache() -> None:
    """
    Clear GPU memory cache and reset CUDA statistics.

    This function should be called periodically to manage GPU memory
    during training or inference processes involving PyTorch models.
    """
    try:
        gc.collect()

        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.reset_peak_memory_stats()

    except ImportError:
        logger.warning("PyTorch not available, skipping CUDA cleanup")
    except RuntimeError as e:
        logger.error("CUDA cleanup failed: %s", str(e))
