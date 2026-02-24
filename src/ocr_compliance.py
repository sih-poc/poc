# ocr_compliance.py

import os
from typing import Set, Dict

import pytesseract
from Levenshtein import ratio
from PIL import Image, ImageOps, ImageFilter
from loguru import logger
import spacy

# Configuration imports - ensure these are defined properly elsewhere in your project
from brand_config import REGULATORY_TEXTS, NET_VOLUME, NUTRITIONAL_FACTS, INGREDIENTS

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_path: str) -> Image.Image:
    """Preprocess an image for optimal OCR performance."""
    try:
        img = Image.open(image_path).convert('L')
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        return img
    except Exception as e:
        logger.error(f"Failed preprocessing image '{image_path}': {e}")
        raise


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR with confidence filtering.

    Returns cleaned lowercase string of extracted text.
    """
    try:
        img = preprocess_image(image_path)
        result = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        confident_texts = [
            word for i, word in enumerate(result['text'])
            if int(result['conf'][i]) > 80 and word.strip()
        ]

        return ' '.join(confident_texts).lower()

    except Exception as e:
        logger.error(f"Failed OCR extraction on '{image_path}': {e}")
        raise


def fuzzy_match(text: str, target: str, threshold_levenshtein: float = 0.2,
                threshold_spacy: float = 0.5) -> bool:
    """
    Combine Levenshtein and spaCy semantic similarity for robust matching.

    Returns True if either method meets its respective threshold.
    """
    text_cleaned = ''.join(c.lower() for c in text if c.isalnum() or c.isspace())
    target_cleaned = ''.join(c.lower() for c in target if c.isalnum() or c.isspace())

    logger.info(f"Comparing '{text_cleaned}' vs '{target_cleaned}'")

    levenshtein_sim = ratio(text_cleaned, target_cleaned)
    logger.info(f"Levenshtein similarity: {levenshtein_sim}")

    result = levenshtein_sim >= threshold_levenshtein

    if not result:
        try:
            nlp = spacy.load("en_core_web_md")
            doc_text = nlp(text_cleaned)
            doc_target = nlp(target_cleaned)

            spacy_sim = doc_text.similarity(doc_target)
            logger.info(f"spaCy similarity: {spacy_sim}")

            result |= (spacy_sim >= threshold_spacy)
        except Exception as e:
            logger.warning(f"spaCy similarity failed: {e}")

    return result


def validate_branding_compliance(image_path: str, label_type: str, region: str) -> Dict: #[str, any]:
    """
    Validate compliance of a product label image against branding requirements.

    Args:
        image_path (str): Path to the label image file.
        label_type (str): Type of label ("front_label", "back_label", or "wraparound").
        region (str): Region identifier for regulatory texts.

    Returns:
        dict: Compliance result with keys:
            - is_compliant (bool)
            - missing_elements (List[str])
            - errors (List[str])
    """
    regulatory = REGULATORY_TEXTS.get(region, "").lower()

    compliance_result = {
        'is_compliant': True,
        'missing_elements': [],
        'errors': []
    }

    # Validate file existence
    if not os.path.exists(image_path):
        error_msg = f"Image file does not exist: {image_path}"
        logger.error(error_msg)
        compliance_result['errors'].append(error_msg)
        compliance_result['is_compliant'] = False
        return compliance_result

    try:
        # Extract text from image
        extracted_text = extract_text_from_image(image_path)
        logger.info(f"Extracted text: {extracted_text}")

        if not extracted_text.strip():
            error_msg = "No readable text found in the image"
            logger.warning(error_msg)
            compliance_result['errors'].append(error_msg)
            compliance_result['is_compliant'] = False
            return compliance_result

        # Define required elements based on label type
        required_elements: Set[str] = set()

        if label_type == "front_label":
            required_elements.update([
                NET_VOLUME.lower(),
                regulatory
            ])
        elif label_type == "back_label":
            required_elements.update([
                NUTRITIONAL_FACTS.lower(),
                INGREDIENTS.lower(),
                regulatory
            ])
        elif label_type == "wraparound":
            required_elements.update([
                NET_VOLUME.lower(),
                regulatory
            ])
        else:
            error_msg = f"Unsupported label type: {label_type}"
            logger.error(error_msg)
            compliance_result['errors'].append(error_msg)
            compliance_result['is_compliant'] = False
            return compliance_result

        # Check required elements with fuzzy matching
        for element in required_elements:
            found = any(
                fuzzy_match(extracted_text, el)
                for el in [element.lower(), element.replace(" ", "").lower()]
            )
            if not found:
                compliance_result['missing_elements'].append(element)
                compliance_result['is_compliant'] = False

    except Exception as e:
        error_msg = f"Error during validation: {str(e)}"
        logger.error(error_msg)
        compliance_result['errors'].append(error_msg)
        compliance_result['is_compliant'] = False

    return compliance_result


# import os
# from typing import Set
#
# import pytesseract
# import spacy
# from Levenshtein import ratio
# from PIL import Image, ImageOps, ImageFilter
# from loguru import logger
#
# from brand_config import REGULATORY_TEXTS, NET_VOLUME, NUTRITIONAL_FACTS, INGREDIENTS
#
# pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'
#
#
# def preprocess_image(image_path):
#     """Preprocess image for optimal OCR performance."""
#     try:
#         img = Image.open(image_path)
#
#         # Convert to grayscale
#         img = img.convert('L')
#
#         # Enhance contrast
#         img = ImageOps.autocontrast(img)
#
#         # Denoise with Gaussian blur
#         img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
#
#         return img
#
#     except Exception as e:
#         logger.error(f"Image preprocessing failed for {image_path}: {e}")
#         raise
#
#
# def extract_text_from_image(image_path) -> str:
#     """
#     Extract text from an image using OCR with confidence filtering.
#     Returns cleaned lowercase string of extracted text.
#     """
#     try:
#         img = preprocess_image(image_path)
#
#         # Using pytesseract's built-in data extraction for better control
#         result = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
#
#         confident_texts = [
#             word for i, word in enumerate(result['text'])
#             if int(result['conf'][i]) > 80 and word.strip()
#         ]
#
#         return ' '.join(confident_texts).lower()
#
#     except Exception as e:
#         logger.error(f"OCR extraction failed for {image_path}: {e}")
#         raise
#
# # def fuzzy_match(text: str, target: str, threshold_levenshtein: float = 0.2,
# #                 threshold_spacy: float = 0.5) -> bool:
# #     """
# #     Combine Levenshtein and spaCy semantic similarity for robust matching.
# #
# #     Returns True if either method meets its respective threshold.
# #     """
# #     text_cleaned = ''.join(c.lower() for c in text if c.isalnum() or c.isspace())
# #     target_cleaned = ''.join(c.lower() for c in target if c.isalnum() or c.isspace())
# #
# #     logger.info(f"Comparing '{text_cleaned}' vs '{target_cleaned}'")
# #
# #     levenshtein_sim = ratio(text_cleaned.lower(), target_cleaned.lower())
# #     logger.info(f"Levenshtein similarity: {levenshtein_sim}")
# #
# #     result = levenshtein_sim >= threshold_levenshtein
# #
# #     if not result:
# #         try:
# #             nlp = spacy.load("en_core_web_md")
# #             doc_text = nlp(text_cleaned.lower())
# #             doc_target = nlp(target_cleaned.lower())
# #
# #             spacy_sim = doc_text.similarity(doc_target)
# #             logger.info(f"spaCy similarity: {spacy_sim}")
# #
# #             result |= (spacy_sim >= threshold_spacy)
# #         except Exception as e:
# #             logger.warning(f"spaCy similarity failed: {e}")
# #
# #     return result
#
# def fuzzy_match(text: str, target: str, threshold_levenshtein: float = 0.2,
#                 threshold_spacy: float = 0.5) -> bool:
#     """
#     Combine Levenshtein and spaCy similarity for robust matching.
#     Returns True if either method meets its respective threshold.
#     """
#
#     # Clean both strings for comparison
#     text_cleaned = ''.join(c.lower() for c in text if c.isalnum() or c.isspace())
#     target_cleaned = ''.join(c.lower() for c in target if c.isalnum() or c.isspace())
#
#     logger.info(f"Comparing: '{text_cleaned}' vs '{target_cleaned}'")
#
#     # Step 1: Levenshtein (edit distance) - good for spelling variations
#     levenshtein_sim = ratio(text_cleaned.lower(), target_cleaned.lower())
#     logger.info(f"Levenshtein similarity: {levenshtein_sim}")
#
#     result = False
#
#     # Check Levenshtein threshold first
#     if levenshtein_sim >= threshold_levenshtein:
#         result = True
#
#     # Step 2: spaCy semantic similarity - understands context and meaning
#     try:
#         import spacy
#         nlp = spacy.load("en_core_web_md")
#
#         doc_text = nlp(text_cleaned.lower())
#         doc_target = nlp(target_cleaned.lower())
#
#         spacy_sim = doc_text.similarity(doc_target)
#         logger.info(f"spaCy similarity: {spacy_sim}")
#
#         if spacy_sim >= threshold_spacy:
#             result = True
#
#     except Exception as e:
#         logger.error(f"spaCy processing failed: {e}")
#
#     return result
#
# def validate_fuzzy_matching(required_elements: Set[str], extracted_text):
#     compliance_result = {
#         'is_compliant': True,
#         'missing_elements': [],
#         'errors': []
#     }
#
#     # Check required elements with fuzzy matching
#     for element in required_elements:
#         found = any(
#             fuzzy_match(extracted_text, el)
#             for el in [element.lower(), element.replace(" ", "").lower()]
#         )
#         if not found:
#             compliance_result['missing_elements'].append(element)
#             compliance_result['is_compliant'] = False
#
#     return compliance_result
#
# def validate_branding_compliance(image_path: str, label_type: str, region: str) -> dict:
#     """
#     Validate compliance of a product label image against branding requirements.
#
#     Args:
#         image_path (str): Path to the label image file.
#         label_type (str): Type of label ("front_label" or "back_label").
#
#     Returns:
#         dict: Compliance result with keys:
#             - is_compliant (bool)
#             - missing_elements (list)
#             - errors (list)
#     """
#     regulatory = REGULATORY_TEXTS.get(region, "")
#
#     compliance_result = {
#         'is_compliant': True,
#         'missing_elements': [],
#         'errors': []
#     }
#
#     # Validate file existence
#     if not os.path.exists(image_path):
#         error_msg = f"Image file does not exist: {image_path}"
#         logger.error(error_msg)
#         compliance_result['errors'].append(error_msg)
#         compliance_result['is_compliant'] = False
#         return compliance_result
#
#     try:
#         # Extract text from image
#         extracted_text = extract_text_from_image(image_path)
#         logger.info(f"Extracted text: {extracted_text}")
#
#         if not extracted_text.strip():
#             error_msg = "No readable text found in the image"
#             logger.warning(error_msg)
#             compliance_result['errors'].append(error_msg)
#             compliance_result['is_compliant'] = False
#             return compliance_result
#
#         # Define required elements based on label type
#         required_elements: Set[str] = set()
#
#         if label_type == "front_label":
#             required_elements.update([
#                 NET_VOLUME.lower(),
#                 regulatory.lower()
#             ])
#         elif label_type == "back_label":
#             required_elements.update([
#                 NUTRITIONAL_FACTS.lower(),
#                 INGREDIENTS.lower(),
#                 regulatory.lower()
#             ])
#         elif label_type == "wraparound":
#             required_elements.update([
#                 NET_VOLUME.lower(),
#                 regulatory.lower()
#             ])
#         else:
#             error_msg = f"Unsupported label type: {label_type}"
#             logger.error(error_msg)
#             compliance_result['errors'].append(error_msg)
#             compliance_result['is_compliant'] = False
#             return compliance_result
#
#         # Check required elements with fuzzy matching
#         for element in required_elements:
#             found = any(
#                 fuzzy_match(extracted_text, el)
#                 for el in [element.lower(), element.replace(" ", "").lower()]
#             )
#             if not found:
#                 compliance_result['missing_elements'].append(element)
#                 compliance_result['is_compliant'] = False
#
#     except Exception as e:
#         error_msg = f"Error during validation: {str(e)}"
#         logger.error(error_msg)
#         compliance_result['errors'].append(error_msg)
#         compliance_result['is_compliant'] = False
#
#     return compliance_result
