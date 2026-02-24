#Centralize the Brand Assets into a Single Source-of truth
from util import get_sku_brief

sku_brief = get_sku_brief()

PRODUCT = "Energy Drink"
BRAND_NAME = "Ctrl+Z Energy"
AUDIENCE = sku_brief["target_audience"]
SUBTITLE = "For the dev who just lost their entire project and needs a reset."
TAGLINE = "Undo your burnout."
STYLE = "Modern tech aesthetic with neon cyberpunk vibes."
LOGO_DESCRIPTION = "A stylized 'Z' shaped like an undo arrow, with a lightning bolt inside."

FLAVOR = ["Berry Reset", "Pixel Punch"]

FONT_STYLE = "Adobe Clean – bold, uppercase letters"
COLOR_PALETTE = {
    "primary": "#E94B3B",  # Error Red
    "secondary": "#007F8C",  # Adobe Teal
    "accent": "#FFFFFF",     # White for contrast
}

NET_VOLUME = "12 FL OZ (355mL)"
KEY_ATTRIBUTES = "180mg Caffeine (from yerba mate), 250mg L-Theanine for clarity, Electrolytes & B-Vitamins, Zero Sugar, Zero Artificial Sweeteners"
INGREDIENTS = "Carbonated Water, Yerba Mate, Citric Acid, Natural Flavors, Taurine, B-Vitamins, Electrolytes"
NUTRITIONAL_FACTS = "Calories: 35 Total Fat: 0g Carbohydrates: 9g Sugars: 0g Protein: 0g"

REGULATORY_TEXTS = {
    "default": "Contains caffeine. Not recommended for children or pregnant women.",
    "US": "Contains caffeine. Not recommended for children or pregnant women.",
    "LATAM": "Contiene cafeína. No recomendado para niños o mujeres embarazadas.",
    "Japan": "カフェインを含みます。お子様や妊婦にはお勧めしません。"
}


# # Centralize the Brand Assets into a Single Source-of truth
# from util import get_sku_brief
#
# sku_brief = get_sku_brief()
#
# # Product Information
# PRODUCT = "Energy Drink"
# BRAND_NAME = "Ctrl+Z Energy"
#
# # Target Audience & Messaging
# AUDIENCE = sku_brief["target_audience"]
# SUBTITLE = "For the dev who just lost their entire project and needs a reset."
# TAGLINE = "Undo your burnout."
#
# # Visual Identity
# STYLE = "Modern tech aesthetic with neon cyberpunk vibes"
# LOGO_DESCRIPTION = "A stylized 'Z' shaped like an undo arrow, with a lightning bolt inside."
#
# # Flavors
# FLAVOR = ["Berry Reset", "Pixel Punch"]
#
# # Typography & Color Palette
# FONT_STYLE = "Adobe Clean – bold, uppercase letters"
#
# COLOR_PALETTE = {
#     "primary": "#E94B3B",  # Error Red
#     "secondary": "#007F8C",  # Adobe Teal
#     "accent": "#FFFFFF",     # White for contrast
# }
#
# # Packaging & Nutritional Info
# NET_VOLUME = "12 FL OZ (355mL)"
# KEY_ATTRIBUTES = (
#     "180mg Caffeine (from yerba mate), "
#     "250mg L-Theanine for clarity, "
#     "Electrolytes & B-Vitamins, "
#     "Zero Sugar, Zero Artificial Sweeteners"
# )
#
# INGREDIENTS = (
#     "Carbonated Water, "
#     "Yerba Mate, "
#     "Citric Acid, "
#     "Natural Flavors, "
#     "Taurine, "
#     "B-Vitamins, "
#     "Electrolytes"
# )
#
# NUTRITIONAL_FACTS = {
#     'Calories': 35,
#     'Total Fat': '0g',
#     'Carbohydrates': '9g',
#     ' Sugars': '0g',
#     'Protein': '0g'
# }
#
# REGULATORY_TEXTS = {
#     "default": "Contains caffeine. Not recommended for children or pregnant women.",
#     "US": "Contains caffeine. Not recommended for children or pregnant women.",
#     "LATAM": "Contiene cafeína. No recomendado para niños o mujeres embarazadas.",
#     "Japan": "カフェインを含みます。お子様や妊婦にはお勧めしません。"
# }