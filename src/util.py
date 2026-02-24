"""
Utility functions for SKU processing and GPU memory management.
"""

import gc
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


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
        file_path = Path("../input/sku_brief.json")
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


# import gc
# import json
# import torch
#
# def get_sku_brief():
#     with open(r"../input/sku_brief.json") as f:
#         return json.load(f)
#
# def clear_cuda_cache():
#     """Clear GPU memory and reset stats."""
#     gc.collect()
#     if torch.cuda.is_available():
#         torch.cuda.synchronize()
#         torch.cuda.empty_cache()
#         torch.cuda.ipc_collect()
#         torch.cuda.reset_peak_memory_stats()