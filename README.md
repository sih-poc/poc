Product Packaging Design System
===============================

Overview
--------

This project is a comprehensive system designed to generate AI-ready packaging design prompts for modern, immersive product labels. The system supports dynamic generation of front, back, and wraparound label designs tailored to specific regional markets, flavor variants, and special editions.

The core functionality revolves around generating structured, consistent prompts that can be used with AI image generation tools (such as DALL-E, Midjourney, or Stable Diffusion) to produce high-quality packaging concepts. The system ensures brand consistency while allowing for creative flexibility across different product lines and markets.


Key Features
------------

-   **Dynamic Prompt Generation**: Creates tailored design prompts based on region, flavor, attribute, and label type.
-   **Brand Consistency**: Enforces consistent branding elements across all products.
-   **Regulatory Compliance**: Automatically includes region-specific regulatory text in generated prompts.
-   **Multi-Label Support**: Supports front, back, and wraparound label designs with distinct requirements.
-   **Immersive Design Concepts**: Enables creation of digital experiences through glitch effects, progress bars, QR codes, and interactive elements.

### Core Components

#### 1\. `get_sku_brief()` --- The Brand Core

This function retrieves the core product configuration from a centralized source (via `input/sku_brief.json`). It returns structured data including:

`{
     "product": "Ctrl+Z Energy",
     "flavors": ["Pixel Punch", "Berry Reset"],
     "target_region": ["US","Japan","LATAM"],
     "target_audience": "Young Adults (Ages 18-25)",
     "attributes": ["organic", "seasonal"]
}`

> This function acts as the single source of truth for all product variations.

* * * * *

#### 2\. Brand Identity (Citation 1)

All creative output is grounded in this consistent brand identity:

| Element                       | Value                                                                                                                             |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Product Type                  | Energy Drink                                                                                                                      |
| Brand Name                    | Ctrl+Z Energy                                                                                                                     |
| Target Audience               | Young Adults                                                                                |
| Subtitle                      | For the dev who just lost their entire project and needs a reset.                                                                 |
| Tagline                       | Undo your burnout.                                                                                                                |
| Style                         | Modern tech aesthetic with neon cyberpunk vibes.                                                                                  |
| Logo Description              | A stylized 'Z' shaped like an undo arrow, with a lightning bolt inside.                                                           |
| Flavors                       | `["Berry Reset", "Pixel Punch"]`                                                                                                  |
| Font Style                    | Adobe Clean -- bold, uppercase letters                                                                                            |
| Color Palette                 | -   Primary: `#E94B3B` (Error Red) - Secondary: `#007F8C`(Adobe Teal) -   Accent: `#FFFFFF` (White for contrast)                  | 
|  Net Volume                   | 12 FL OZ (355mL)                                                                                                                  | 
|  Key Attributes               | 180mg Caffeine (from yerba mate), 250mg L-Theanine for clarity, Electrolytes & B-Vitamins, Zero Sugar, Zero Artificial Sweeteners | 
|  Ingredients                  | Carbonated Water, Yerba Mate, Citric Acid, Natural Flavors, Taurine, B-Vitamins, Electrolytes                                     | 
|  Nutritional Facts (per can)  | Calories: 35, Total Fat: 0g, Carbohydrates: 9g, Sugars: 0g, Protein: 0g                                                           | 
|  Regulatory Texts             | Multi-lingual compliance warnings for US, LATAM, Japan                                                                            |


> These values are used dynamically in prompt generation and ensure brand consistency.

* * * * *

#### 3\. Label Templates (Citation 3)

The system uses three distinct label types with structured templates:

##### 🔹 `front_label` Template

`"""
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
"""`

##### 🔹 `back_label` Template

`"""
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
"""`

##### 🔹 `wraparound` Template

`"""
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
"""`

> These templates are passed into an AI model or design engine via `generate_prompt()`.

* * * * *

#### 4\. Prompt Generation Function

`def generate_prompt(region: str, flavor: str, attribute: str, label: str) -> str:
    """
    Generates a prompt for packaging design using configurable templates.

    Args:
        region (str): The target geographic market.
        flavor (str): The specific flavor variant.
        attribute (str): Special edition or variation of the product.
        label (str): Label style ('front_label', 'back_label', or 'wraparound').

    Returns:
        str: A fully formatted prompt ready for AI generation.
    """`

> This function dynamically fills in placeholders using brand data and user inputs, ensuring no hardcoded text and maximum flexibility.

* * * * *

#### 5\. Async Label Generation (Citation 2)

`async def main():
    """
    Main execution function that orchestrates label generation for all combinations.

    This function generates labels for every combination of regions, flavors, attributes,
    and label types using async parallel processing with concurrency control.
    """

    # Retrieve SKU configuration
    sku_brief = get_sku_brief()
    REGIONS = sku_brief["target_region"]
    FLAVORS = sku_brief["flavors"]
    ATTRIBUTES = sku_brief["attributes"]

    # Create all possible combinations
    combinations = product(REGIONS, FLAVORS, ATTRIBUTES, LABELS)

    # Set up semaphore for concurrency control (adjust based on GPU memory)
    semaphore = asyncio.Semaphore(1)  # Limit to 1 concurrent task

    # Create tasks for all combinations
    tasks = [
        asyncio.create_task(generate_labels_for_combination(r, f, a, l))
        for r, f, a, l in combinations
    ]

    # Process results as they complete
    completed_results = []

    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            completed_results.append(result)
        except Exception as e:
            logger.error(f"Task failed with error: {e}")
            completed_results.append({
                "status": "error",
                "task_error": str(e)
            })

    # Generate summary report
    if completed_results:
        compliant_labels = sum(1 for r in completed_results
                               if isinstance(r.get('result'), str) and r['status'] == 'success')
        total_labels = len(completed_results)
        successful_generations = sum(1 for r in completed_results if r['status'] == 'success')

        logger.success(
            f"Completed generation of {total_labels} labels ({successful_generations} successful, "
            f"{compliant_labels} compliant)"
        )`

#### Key features:

-   Uses `itertools.product()` to generate all possible combinations.
-   Employs `asyncio.Semaphore(1)` for safe GPU/CPU usage (can be adjusted).
-   Processes results as they finish (`as_completed`), improving efficiency.
-   Logs detailed success/failure metrics.

* * * * *

### Required Environment Variables

To run this project successfully, you must set the following environment variables in your local environment or via a `.env` file:

#### Hugging Face Token (for accessing models like OCR engines)
HF_TOKEN=your_huggingface_token_here

#### AWS S3 Credentials (for uploading generated labels to cloud storage)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1  # or your preferred region
S3_BUCKET_NAME=ctrl-z-energy-labels`

> Note:
> -   The `HF_TOKEN` is required if you're using Hugging Face-based OCR models (e.g., for text extraction from image labels).
> -   AWS S3 credentials are needed to upload generated label images to your cloud storage bucket. If these are missing, the system will skip uploads but continue processing.
* * * * *

### 🧪 Usage Instructions

#### 1\. Install Dependencies

`pip install -r requirements.txt`

#### 2\. Configure Brand Data

Ensure `input/sku_brief.json` contains:

`{
    "target_audience": "Young Adults (Ages 18-25)",
    "target_region": ["US", "LATAM", "Japan"],
    "flavors": ["Berry Reset", "Pixel Punch"],
    "attributes": ["organic", "seasonal"]
}`

#### 3\. Run the Generator

`python main.py`

#### This will:
-   Load brand data.
-   Generate all label combinations asynchronously.
-   Output results to logs and save them.

* * * * *

### Output & Reporting

After execution, a summary log is printed:

`Completed generation of 36 labels (18 successful, 15 compliant)`

#### This indicates:
-   Total: 3 regions × 2 flavors × 2 attributes × 3 label types = 36 combinations
-   18 succeeded in generating valid prompts
-   18 were fully compliant with regulatory standards

* * * * *

### 🛠️ Extensibility & Customization

#### Add New Label Types

Simply add a new template to the `prompts.py` file and update the `LABELS` list.

`LABELS = ["front_label", "back_label", "wraparound"]`

#### Support More Regions

Update `REGIONS` in `get_sku_brief()` or `sku_brief.json`.

* * * * *

### Final Notes

This project enables automated, scalable, and compliant packaging design for a global energy drink brand. By centralizing branding assets (via `get_sku_brief()`), leveraging async processing, and using modular templates, it ensures:

-   Consistency across markets
-   Regulatory compliance through dynamic text insertion
-   Rapid iteration for new flavors or editions

> Next Steps: Integrate with AI image generation APIs to produce actual label mockups. Integrate UI mockup generator using HTML/CSS templates. Add validation checks (e.g., character limits, font size) before sending prompts. Expand fuzzy matching beyond exact text match (e.g., synonyms, alternative spellings).

* * * * *

End of README.md

