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

from config.config import MODEL_NAME, CACHE_DIR, TORCH_DTYPE, DEVICE, FORMATS, NEGATIVE_PROMPT, OUTPUT_DIR, \
    S3_OUTPUT_DIR
from src.generate_prompt import generate_prompt
from src.ocr_compliance import validate_branding_compliance
from src.save_to_s3 import S3Uploader, save_to_s3
from src.util import clear_cuda_cache

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
                num_inference_steps=20,
                guidance_scale=1.25
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


