# config.py
import getpass
import os
import torch
from accelerate import Accelerator
from dotenv import load_dotenv
from huggingface_hub import login
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Initialize Accelerator for distributed training (can be used even on CPU)
accelerator = Accelerator()

# ========================
# Directories & Paths
# ========================
OUTPUT_DIR = os.path.abspath(r"./output")
S3_OUTPUT_DIR = r"output"
CACHE_DIR = r"D:\.cache\huggingface\hub"

# ========================
# Model Selection
# ========================
MODEL_NAME = "unsloth/Z-Image-Turbo-unsloth-bnb-4bit"
logger.info(f"Model selected: {MODEL_NAME}")

# ========================
# Device and Dtype Configuration
# ========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.bfloat16 if torch.cuda.is_available() else torch.float32

logger.info(f"CUDA available: {torch.cuda.is_available()}")
logger.info(f"Device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    total_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    logger.info(f"Current GPU: {gpu_name}")
    logger.info(f"Total GPU memory: {total_memory_gb:.2f} GB")

# ========================
# Performance Tuning Environment Variables
# ========================
os.environ.update({
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    "HF_XET_HIGH_PERFORMANCE": "True",
    "HF_XET_RECONSTRUCT_WRITE_SEQUENTIALLY": "True",
    "HF_HUB_DISABLE_TELEMETRY": "True"
})

# Optional optimization flag (commented out by default)
# torch.backends.cuda.matmul.allow_tf32 = True

# ========================
# Hugging Face Authentication
# ========================

# Check if HF_TOKEN is set in environment
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    logger.warning("HF_TOKEN not found in environment variables.")
    # Prompt user to enter token interactively
    HF_TOKEN = getpass.getpass("Please enter your Hugging Face token: ").strip()

    env_path = ".env"
    try:
        with open(env_path, "a") as f:
            f.write(f"\nHF_TOKEN={HF_TOKEN}")
        logger.info(f"HF_TOKEN saved to {env_path}")
    except Exception as e:
        logger.warning(f"Failed to save HF_TOKEN to .env: {e}")

    if not HF_TOKEN:
        raise ValueError("Hugging Face token is required. Aborting.")

# Authenticate using the token (from env or user input)
try:
    login(token=HF_TOKEN)
except Exception as e:
    logger.error(f"Failed to authenticate with Hugging Face: {e}")
    raise

logger.success("Hugging Face token authenticated.")

# ========================
# Prompt and Image Format Configuration
# ========================
FORMATS = {
    "front_label": (1024, 1024),   # square aspect ratio
    "back_label": (768, 1344),     # vertical portrait (9:16)
    "wraparound": (1344, 768),     # horizontal landscape (16:9)
}

NEGATIVE_PROMPT = (
    "blurry, unfocused, deviate from the parameters, extra words, misspellings, inconsistent"
)


