"""
Generate prompts tailored to specific labels using configurable prompt templates.
Supports modular composition of packaging designs across multiple label types and regions.

TODO: support external template files or YAML-based configuration
"""

from brand_config import (
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



# from brand_config import REGULATORY_TEXTS, AUDIENCE, PRODUCT, BRAND_NAME, SUBTITLE, LOGO_DESCRIPTION, NET_VOLUME, \
#     FONT_STYLE, TAGLINE, KEY_ATTRIBUTES, INGREDIENTS, NUTRITIONAL_FACTS
#
#
# def generate_prompt(region: str, flavor: str, attribute: str, label: str) -> str:
#     regulatory = REGULATORY_TEXTS.get(region, "")
#     # ColorPalette: {COLOR_PALETTE}
#     if label == 'front_label':
#         prompt = f'''Visual Concept: Create a vibrant, modern {attribute} edition of an {PRODUCT} packaging design
#         that's highly specialized to {AUDIENCE} in this specific {region} market using the following parameters:
#
#         Title: "{BRAND_NAME}"
#         Subtitle: "{SUBTITLE}"
#         Logo Description: {LOGO_DESCRIPTION}
#         Net Volume (bottom of product): "{NET_VOLUME}"
#
#         Font: {FONT_STYLE}
#         Tagline: "{TAGLINE}"
#
#         Key Attributes (icon-based):
#         - “180mg Caffeine (from yerba mate)”
#         - “250mg L-Theanine for clarity”
#         - “Electrolytes & B-Vitamins”
#         - “Zero Sugar, Zero Artificial Sweeteners”
#
#         Flavor: "{flavor}"
#         Net Volume: "{NET_VOLUME}"
#
#         Regulatory Info (small, discreet at bottom):{regulatory}”
#
#         Write in clear language. Only latin characters and numbers. Only complete words, and measurements. Be consistent across products. Do not forget to add Regulatory Compliance.
#         '''
#         return prompt
#
#     elif label == 'back_label':
#         prompt = f'''Visual Concept: vibrant, modern nutritional label and ingredient list. Next to it is a vertical scroll
#         of a digital timeline showing the user’s journey. The digital timeline design uses glitch effects and progress bars.
#
#         Region: {region}
#         Audience: {AUDIENCE}
#         Market: {attribute}
#
#         - Ingredients List (English): {INGREDIENTS}
#
#         - Allergen Info:
#           “Contains: None. Made in a facility that processes tree nuts.”
#
#         - Nutrition Facts (per can): {NUTRITIONAL_FACTS}
#
#         - QR Code:
#           Links to “How We Prevented Creative Burnout” blog.
#
#         Regulatory Info (small, discreet at bottom):{regulatory}”
#
#         Write in clear language. Only latin characters and numbers. Only complete words, and measurements. Be consistent across products. Do not forget to add Regulatory Compliance.
#         '''
#         return prompt
#
#     else:  # label=='wraparound':
#         prompt = f'''Visual Concept: Design a wraparound label for vibrant, modern {attribute} edition of an {PRODUCT}
#         packaging design highly specialized to {AUDIENCE} in this specific {region} market that transforms the can
#         into an immersive digital experience. Fill the space as if the label is laying flat.
#
#         {PRODUCT} INFO:
#         Title (middle of product): "{BRAND_NAME}"
#         Flavor: "{flavor}"
#         Subtitle (underneath title): "{SUBTITLE}"
#         Tagline (underneath title): "{TAGLINE}"
#         Logo Description: {LOGO_DESCRIPTION}
#         Net Volume (bottom of product): "{NET_VOLUME}"
#         Key Attributes (icon-based): "{KEY_ATTRIBUTES}"
#         Regulatory Info (small, discreet at bottom):{regulatory}”
#
#         Write in clear language. Only latin characters and numbers. Only complete words, and measurements. Be consistent across products. Do not forget to add Regulatory Compliance.
#         '''
#         return prompt
#
# # def generate_prompt(region: str, flavor: str, attribute: str, label: str) -> str:
# #     if label=='front_label':
# #         return f'''Design a bold, high-contrast front label for Ctrl+Z Energy in a modern cyberpunk style.
# #         Use Adobe Clean font in bold uppercase letters with sharp edges.
# #         Feature the brand name 'CTRL+Z ENERGY' prominently at the top in neon-lit white text against a deep black
# #         background. Below it, display the subtitle: 'For the dev who just lost their entire project and needs a reset.'
# #         Centered beneath is the stylized logo—a glowing 'Z' shaped like an undo arrow with a lightning bolt
# #         inside—pulsing in electric red (#E94B3B) and teal (#007F8C). Include the flavor name ('Berry Reset')
# #         in smaller neon text at the bottom. Use dynamic digital glitch effects, subtle circuit board patterns
# #         in the background, and a faint holographic glow to evoke a tech-reboot aesthetic. Ensure all elements
# #         are clean, futuristic, and instantly recognizable as an energy drink for coders.'''
# #     elif label=='back_label':
# #         return f'''Create a back-label layout for Ctrl+Z Energy with a sleek, data-driven cyberpunk design.
# #         Use Adobe Clean font in bold uppercase letters on a dark charcoal background with neon accents.
# #         At the top, display the tagline 'Undo your burnout.' in white and red. Below, list key attributes:
# #         '180mg Caffeine (from yerba mate), 250mg L-Theanine for clarity, Electrolytes & B-Vitamins, Zero Sugar,
# #         Zero Artificial Sweeteners'—each item highlighted with a glowing neon bullet point. Include the full
# #         ingredients list in smaller white text, followed by nutritional facts:
# #         'Calories: 35 | Total Fat: 0g | Carbohydrates: 9g | Sugars: 0g | Protein: 0g'.
# #         At the bottom, place regulatory text (US version) with a subtle digital font. Add a minimalist circuit-line
# #         border and faint binary code patterns in the background to maintain brand consistency. Ensure readability
# #         while preserving high-tech visual flair.'''
# #     elif label=='wraparound':
#
# # The design should flow seamlessly around the 12 FL OZ can, featuring a dynamic gradient from deep
# # black to electric red (#E94B3B) and teal (#007F8C), evoking a neon-lit server rack or data stream.
# # On one side, place the front-label elements (brand name, logo, subtitle). As the label wraps around,
# # introduce animated-style glitch effects that reveal flavor-specific details: {flavor} with pixelated graphics. Include a continuous digital countdown timer motif
# # or binary code scroll along the sides to symbolize ‘resetting’ time. At the bottom, integrate the {NUTRITIONAL_FACTS}
# # and {regulatory} text in clean white font against a dark band. Use subtle holographic textures and light
# # reflections to enhance realism under ambient lighting—making it feel like a high-tech device from 2087.
# #         return f'''Design a wraparound label for Ctrl+Z Energy that transforms the can into an immersive digital
# #         experience. The design should flow seamlessly around the 12 FL OZ can, featuring a dynamic gradient from deep
# #         black to electric red (#E94B3B) and teal (#007F8C), evoking a neon-lit server rack or data stream.
# #         On one side, place the front-label elements (brand name, logo, subtitle). As the label wraps around,
# #         introduce animated-style glitch effects that reveal flavor-specific details: {flavor} with pixelated graphics. Include a continuous digital countdown timer motif
# #         or binary code scroll along the sides to symbolize ‘resetting’ time. At the bottom, integrate the {NUTRITIONAL_FACTS}
# #         and {REGULATORY} text in clean white font against a dark band. Use subtle holographic textures and light
# #         reflections to enhance realism under ambient lighting—making it feel like a high-tech device from 2087.'''
#
# # def generate_prompt(region: str, flavor: str, attribute: str, label: str) -> str:
# #     regulatory = REGULATORY_TEXTS.get(region, "")
# #
# #     prompt = f'''
# #     Create a vibrant, modern {attribute} editions of {PRODUCT} packaging design highly specialized to {AUDIENCE} in this specific market {region} using the following parameters:
# #     {PRODUCT} INFO:
# #     Title (middle of product): "{BRAND_NAME}"
# #     Flavor: "{flavor}"
# #     Subtitle (underneath title): "{SUBTITLE}"
# #     Tagline (underneath title): "{TAGLINE}"
# #     Logo Description: {LOGO_DESCRIPTION}
# #     Net Volume (bottom of product): "{NET_VOLUME}"
# #     Key Attributes (icon-based): "{KEY_ATTRIBUTES}"
# #     Regulatory Compliance (bottom of product): "{regulatory}"
# #
# #     Use this Color Palette (do not include text in design): {COLOR_PALETTE} and Font Style (do not include text in design): {FONT_STYLE} for this Design Style: {STYLE}.
# #     Please include {NUTRITIONAL_FACTS} and {INGREDIENTS} for back_label.
# #     Write in clear language. Only latin characters and numbers. Only complete words, and measurements. Be consistent across products. Do not forget to add Regulatory Compliance.
# #     '''
# #
# #     return prompt.strip()
#
#
