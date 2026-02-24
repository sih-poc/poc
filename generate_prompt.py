"""
Generate prompts tailored to specific labels using configurable prompt templates.
Supports modular composition of packaging designs across multiple label types and regions.

TODO: support external template files or YAML-based configuration
"""

from config.brand_config import (
    REGULATORY_TEXTS, AUDIENCE, PRODUCT, BRAND_NAME, SUBTITLE,
    LOGO_DESCRIPTION, NET_VOLUME, FONT_STYLE, TAGLINE, KEY_ATTRIBUTES,
    INGREDIENTS, NUTRITIONAL_FACTS
)

# Template Definitions - Configurable prompt structures
TEMPLATES = {
    'front_label': '''
Design a vibrant, modern {attribute} edition of an {PRODUCT} packaging design that's highly specialized
specifically for {AUDIENCE} in the {region} market using the following parameters:

Title: "{BRAND_NAME}"
Subtitle: "{SUBTITLE}"
Logo Description: {LOGO_DESCRIPTION}
Net Volume (bottom of product): "{NET_VOLUME}"

Font: {FONT_STYLE}
Tagline: "{TAGLINE}"

Key Attributes:
{key_attributes_list}

Flavor: "{flavor}"
Net Volume: "{NET_VOLUME}"

Regulatory Info:
{regulatory_text}

Write in clear language. Only latin characters and numbers. Only complete words, and measurements.
Be consistent across products. Do not forget to add the Regulatory Info.
''',

    'back_label': '''
Design a vibrant, modern nutritional facts label and ingredient list packaging design that's highly specialized
specifically for {AUDIENCE} in the {region} market using the following parameters:

Region: {region}
Audience: {AUDIENCE}
Market: {attribute}

Ingredients List (English): {ingredients_list}

Allergen Info:
Contains: None. Made in a facility that processes tree nuts.

Nutrition Facts (per can): {nutritional_facts}

QR Code:
Links to “How We Prevented Creative Burnout” blog.

Regulatory Info:
{regulatory_text}

Next to it is a vertical scroll of a digital timeline showing the user’s journey. The digital timeline design uses 
glitch effects and progress bars. Write in clear language. Only complete words, 
and measurements. Be consistent across products. Do not forget to add the Regulatory Info.
''',

    'wraparound': '''
Design a wraparound label for vibrant, modern {attribute} edition of an {PRODUCT} packaging design highly specialized 
to {AUDIENCE} in this specific {region} market that transforms the can into an immersive digital experience. Fill the 
space as if the label is laying flat.

{PRODUCT} INFO:
Title (middle of product): "{BRAND_NAME}"
Flavor: "{flavor}"
Subtitle (underneath title): "{SUBTITLE}"
Tagline (underneath title): "{TAGLINE}"
Logo Description: {LOGO_DESCRIPTION}
Net Volume (bottom of product): "{NET_VOLUME}"
Key Attributes (icon-based): "{KEY_ATTRIBUTES}"

Regulatory Info:
{regulatory_text}

Write in clear language. Only latin characters and numbers. Only complete words, and measurements.
Be consistent across products. Do not forget to add the Regulatory Info.
'''
}


def generate_prompt(region: str, flavor: str, attribute: str, label: str) -> str:
    """
    Generates a prompt for packaging design using configurable templates.

    Args:
        region (str): The target geographic market.
        flavor (str): The specific flavor variant.
        attribute (str): Special edition or variation of the product.
        label (str): Label style ('front_label', 'back_label', or 'wraparound').

    Returns:
        str: A formatted prompt string suitable for use in AI generation tools.

    Raises:
        ValueError: If an unsupported label type is provided or required data is missing.
    """

    if label not in TEMPLATES:
        raise ValueError(f"Unsupported label type: '{label}'. Expected 'front_label', 'back_label', or 'wraparound'.")

    regulatory_text = REGULATORY_TEXTS.get(region, "")

    # Format the key attributes list (if needed)
    formatted_key_attributes = '\n'.join([f"- “{attr.strip()}”" for attr in KEY_ATTRIBUTES.split('\n')]) \
        if isinstance(KEY_ATTRIBUTES, str) and '\n' in KEY_ATTRIBUTES else f"- \"{KEY_ATTRIBUTES}\""

    # Prepare template arguments
    prompt_args = {
        'label': label,
        'region': region,
        'flavor': flavor,
        'attribute': attribute,
        'AUDIENCE': AUDIENCE,
        'PRODUCT': PRODUCT,
        'BRAND_NAME': BRAND_NAME,
        'SUBTITLE': SUBTITLE,
        'LOGO_DESCRIPTION': LOGO_DESCRIPTION,
        'NET_VOLUME': NET_VOLUME,
        'FONT_STYLE': FONT_STYLE,
        'TAGLINE': TAGLINE,
        'ingredients_list': INGREDIENTS,
        'nutritional_facts': NUTRITIONAL_FACTS,
        'regulatory_text': regulatory_text,
        'key_attributes_list': formatted_key_attributes
    }

    # Handle special cases for template variables
    if label == 'front_label':
        prompt_args['KEY_ATTRIBUTES'] = KEY_ATTRIBUTES

    elif label == 'wraparound':
        prompt_args['KEY_ATTRIBUTES'] = KEY_ATTRIBUTES

    try:
        prompt = TEMPLATES[label].format(**prompt_args).strip()
        return prompt
    except KeyError as e:
        raise ValueError(f"Missing required variable in template: {e}")


