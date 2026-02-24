import asyncio
from itertools import product
from loguru import logger
from generate_label import generate_labels
from util import get_sku_brief

# Constants for label types
LABELS = ['front_label', 'back_label', 'wraparound']


async def generate_labels_for_combination(region: str, flavor: str, attribute: str, label: str) -> dict:
    """
    Generate a label for a specific combination of region, flavor, attribute, and label type.

    Args:
        region (str): Target geographic region
        flavor (str): Flavor variant
        attribute (str): Product attribute
        label (str): Label type to generate

    Returns:
        dict: Result containing generation status and metadata
    """
    try:
        result = await generate_labels(region, flavor, attribute, label)
        logger.success(
            f"{label} generation complete for Region: {region} | Flavor: {flavor} | Attribute: {attribute}"
        )
        return {
            "status": "success",
            "region": region,
            "flavor": flavor,
            "attribute": attribute,
            "label_type": label,
            "result": result
        }
    except Exception as e:
        logger.error(
            f"Error generating {label} for Region: {region} | Flavor: {flavor} | Attribute: {attribute}. Error: {e}"
        )
        return {
            "status": "error",
            "region": region,
            "flavor": flavor,
            "attribute": attribute,
            "label_type": label,
            "error": str(e)
        }


async def main():
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
    semaphore = asyncio.Semaphore(1)

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
        )


if __name__ == "__main__":
    asyncio.run(main())

# import asyncio
# from itertools import product
# from loguru import logger
# from generate_label import generate_labels#, generator_instance
# from util import get_sku_brief
#
# LABELS = ['front_label', 'back_label', 'wraparound']
#
# sku_brief = get_sku_brief()
# REGIONS = sku_brief["target_region"]
# FLAVORS = sku_brief["flavors"]
# ATTRIBUTES = sku_brief["attributes"]
#
# semaphore = asyncio.Semaphore(1)  # Adjust concurrency based on GPU memory
#
#
# async def generate_labels_for_combination(region, flavor, attribute, label):
#     async with semaphore:
#         try:
#             result = await generate_labels(region, flavor, attribute, label)
#             logger.success(
#                 f"{label} generation complete for Region: {region} | Flavor: {flavor} | Attribute: {attribute} ")
#             return result
#         except Exception as e:
#             logger.error(
#                 f"Error generating {label} for Region: {region} | Flavor: {flavor} | Attribute: {attribute}. Error: {e}")
#             raise
#
#
# async def main():
#     combinations = product(REGIONS, FLAVORS, ATTRIBUTES, LABELS)
#
#     tasks = [
#         asyncio.create_task(generate_labels_for_combination(r, f, a, l))
#         for r, f, a, l in combinations
#     ]
#
#     # Process results as they complete
#     completed_results = []
#     for task in asyncio.as_completed(tasks):
#         try:
#             result = await task
#             completed_results.append(result)
#         except Exception as e:
#             logger.error(f"Task failed with error: {e}")
#
#     # Report summary
#     if completed_results:
#         compliant_labels = sum(1 for r in completed_results if isinstance(r, str))
#         total_labels = len(completed_results)
#         logger.success(f"Completed generation of {total_labels} labels ({compliant_labels} compliant)")
#
#     # # Generate a single label
#     # path, compliance = await generator_instance.process_label(
#     #     "US",
#     #     "original",
#     #     "front",
#     #     "front_label"
#     # )
#
#     # # Or generate multiple labels in parallel
#     # results = await generate_labels(
#     #     # "US",
#     #     # "original",
#     #     # "front",
#     #     # ["front_label", "back_label"]
#     #     REGIONS,
#     #     FLAVORS,
#     #     ATTRIBUTES,
#     #     LABELS,
#     # )
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
