"""
TODO:
1. Add Unit Tests / Mock Pipeline for CI/CD
2. Use Configurable Environment Variables
"""

import os

import torch
from PIL import Image
from diffusers import DiffusionPipeline
from loguru import logger

from config import MODEL_NAME, CACHE_DIR, TORCH_DTYPE, DEVICE, NEGATIVE_PROMPT, FORMATS, OUTPUT_DIR
from generate_prompt import generate_prompt
from ocr_compliance import validate_branding_compliance
from save_to_s3 import save_to_s3, S3Uploader
from config import S3_OUTPUT_DIR
from util import clear_cuda_cache

# Global pipeline instance for lazy loading.
PIPELINE = None


def get_pipeline():
    """Lazy-load diffusion pipeline once."""
    global PIPELINE

    if PIPELINE is not None:
        return PIPELINE

    logger.info("Loading diffusion pipeline for the first time...")
    try:
        pipe = DiffusionPipeline.from_pretrained(
            MODEL_NAME,
            cache_dir=CACHE_DIR,
            low_cpu_mem_usage=True,
            torch_dtype=TORCH_DTYPE,
        ).to(DEVICE)

        if torch.cuda.is_available():
            pipe.enable_attention_slicing()

        PIPELINE = pipe
        logger.success("Pipeline loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load pipeline due to error: {e}")
        raise

    return PIPELINE


def generate_label(label: str, prompt: str) -> Image.Image:
    """Generate label image using diffusion model."""
    pipe = get_pipeline()
    width, height = FORMATS[label]

    try:
        with torch.inference_mode():
            output = pipe(
                prompt=prompt,
                negative_prompt=NEGATIVE_PROMPT,
                width=width,
                height=height,
                num_inference_steps=10,
                guidance_scale=1.0
            )
        image = output.images[0]
        return image

    except Exception as e:
        logger.error(f"Label generation failed for '{label}': {e}")
        raise

    finally:
        clear_cuda_cache()


async def generate_labels(region: str, flavor: str, attribute: str, label: str) -> str:
    """Generate branded labels and validate compliance."""
    base_output_path = os.path.join(OUTPUT_DIR, region, flavor, attribute, label)
    output_file_path = f"{base_output_path}.png"

    uploader = S3Uploader()
    s3_output_path = f"{S3_OUTPUT_DIR}/{region}/{flavor}/{attribute}/{label}"

    try:
        logger.info(f"Generating '{label}' for Region: {region}, Flavor: {flavor}, Attribute: {attribute}")
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        prompt = generate_prompt(region, flavor, attribute, label)
        image = generate_label(label, prompt)

        # Save locally
        image.save(output_file_path, format="PNG", quality=90)
        logger.success(f"Label '{label}' saved to {output_file_path}")

        compliance_result = validate_branding_compliance(output_file_path, label, region)

        if not compliance_result['is_compliant']:
            missing_elements = ", ".join(compliance_result['missing_elements'])
            logger.warning(
                f"Compliance issues detected in '{label}': Missing elements [{missing_elements}]"
            )
            return output_file_path
        else:
            logger.info(f"Label '{label}' passed OCR compliance check")

            # Save to S3
            try:
                save_to_s3(output_file_path, s3_output_path)
                logger.success("Uploaded label successfully to S3")
            except ImportError as e:
                logger.warning(f"Module 'save_to_s3' missing: Skipping upload. Error: {e}")
            except Exception as e:
                logger.error(f"Upload failed with error: {e}")

            return output_file_path

    except Exception as e:
        logger.error(f"Failed generation of label '{label}' due to error: {str(e)}")
        raise



# import torch
# from PIL import Image
# from diffusers import DiffusionPipeline
# from config import MODEL_NAME, CACHE_DIR, TORCH_DTYPE, DEVICE, NEGATIVE_PROMPT
# from ocr_compliance import validate_branding_compliance
# from generate_prompt import generate_prompt
# from src.config import S3_OUTPUT_DIR
# from util import clear_cuda_cache, get_sku_brief
# from loguru import logger
# import os
# from functools import lru_cache
# from config import FORMATS, OUTPUT_DIR
# from save_to_s3 import save_to_s3
#
# sku_brief = get_sku_brief()
# AUDIENCE = sku_brief["target_audience"]
#
# PIPELINE = None
#
# async def generate_labels(region: str, flavor: str, attribute: str, label: str) -> str:
#     output_path = os.path.join(OUTPUT_DIR, region, flavor, attribute, label)
#     S3_output_path = os.path.join(S3_OUTPUT_DIR, region, flavor, attribute, label)
#
#     try:
#         logger.info(f"Generating {label} for Region: {region} | Flavor: {flavor} | Attribute: {attribute}")
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#         prompt = generate_prompt(region, flavor, attribute, label)
#
#         # Generate the image
#         image = generate_label(label, prompt)
#
#         # Save locally
#         full_output_path = f"{output_path}.png"
#         image.save(full_output_path, format="PNG", quality=90)
#         logger.success(f"Saved {label} to {output_path}")
#
#         # Validate compliance in a thread-safe way
#         compliance_result = validate_branding_compliance(full_output_path, label, region)
#
#         if not compliance_result['is_compliant']:
#             missing_elements = ", ".join(compliance_result['missing_elements'])
#             logger.warning(
#                 f"Compliance issue found in {label} Region: {region} | Flavor: {flavor} | Attribute: {attribute}: Missing elements: {missing_elements}"
#             )
#             return full_output_path
#         else:
#             logger.info(f"Label {label} passed OCR compliance check")
#             # Save to S3
#             try:
#                 save_to_s3(f"{S3_output_path}.png", label, output_path)
#                 logger.success(f"Saved {label} to S3 Bucket")
#             except ImportError:
#                 logger.warning("save_to_s3 module not found. Skipping upload.")
#
#             return full_output_path
#
#     except Exception as e:
#         logger.error(f"Failed generation of label '{label}' due to error: {e}")
#         raise
#
#
# @lru_cache(maxsize=1)
# def get_pipeline():
#     """
#     Lazy load diffusion pipeline to avoid repeated initializations.
#     Only loads once and caches globally.
#     """
#     global PIPELINE
#
#     if PIPELINE is None:
#         logger.info("Loading diffusion pipeline for the first time...")
#         try:
#             PIPELINE = DiffusionPipeline.from_pretrained(
#                 MODEL_NAME,
#                 cache_dir=CACHE_DIR,
#                 low_cpu_mem_usage=True,
#                 torch_dtype=TORCH_DTYPE,  # Changed from TORCH_DTYPE
#             ).to(DEVICE)
#
#             if hasattr(torch.cuda, 'is_available') and torch.cuda.is_available():
#                 PIPELINE.enable_attention_slicing()  # Memory optimization
#
#             logger.success("Pipeline loaded successfully.")
#         except Exception as e:
#             logger.error(f"Failed to load pipeline: {e}")
#             raise
#
#     return PIPELINE
#
#
# def generate_label(label: str, prompt: str) -> Image.Image:
#     """
#     Generates a label using the diffusion model based on given prompt and label dimensions.
#
#     :param label: Label type (e.g., front_label)
#     :param prompt: Prompt string used for generation
#     :return: PIL Image object of generated label
#     """
#
#     pipe = get_pipeline()
#
#     try:
#         width, height = FORMATS[label]
#         with torch.inference_mode():
#             output = pipe(
#                 prompt=prompt,
#                 negative_prompt=NEGATIVE_PROMPT,
#                 width=width,
#                 height=height,
#                 num_inference_steps=10,
#                 guidance_scale=1.0 #1.0
#             )
#         image = output.images[0]
#         return image
#
#     except Exception as e:
#         logger.error(f"Error during label generation for '{label}': {e}")
#         raise
#
#     finally:
#         clear_cuda_cache()
