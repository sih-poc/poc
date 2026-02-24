import os
from getpass import getpass

import boto3
import botocore.exceptions
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class S3Uploader:
    """S3 uploader class for handling file uploads with enhanced error handling."""

    def __init__(self):
        self.region_name = os.environ.get("S3_REGION")
        if not self.region_name:
            raise ValueError("S3_REGION environment variable is required")

        self.bucket_name = os.environ.get("S3_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")

        credentials = {
            'aws_access_key_id': os.environ.get("AWS_ACCESS_KEY_ID"),
            'aws_secret_access_key': os.environ.get("AWS_SECRET_ACCESS_KEY")
        }

        # If missing, prompt user to input them
        if not credentials['aws_access_key_id'] or not credentials['aws_secret_access_key']:
            logger.warning("AWS credentials not found in environment. Please provide them.")
            aws_access_key_id = getpass("Enter AWS Access Key ID: ")
            aws_secret_access_key = getpass("Enter AWS Secret Access Key: ")

            # Optionally save to .env file (optional step)
            self._save_to_env(aws_access_key_id, aws_secret_access_key)

        # Validate credentials
        if not credentials['aws_access_key_id'] or not credentials['aws_secret_access_key']:
            raise ValueError("AWS credentials are required")

        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region_name,
                **credentials
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3 bucket.

        Args:
            local_path (str): Local path of the file to upload
            s3_key (str): Destination key in S3

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not local_path or not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file '{local_path}' does not exist")

            if not s3_key:
                raise ValueError("S3 key cannot be empty")

            logger.info(f"Uploading {local_path} to s3")

            # Upload the file
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"Successfully uploaded {local_path} to s3:")
            return True

        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Client Error ({error_code}): {error_message}")
            return False

        except botocore.exceptions.NoCredentialsError:
            logger.error("AWS credentials not found")
            return False

        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False

    def _save_to_env(self, access_key, secret_key):
        """Save AWS credentials to .env file (optional)."""
        env_path = ".env"
        with open(env_path, "a") as f:
            f.write(f"\nAWS_ACCESS_KEY_ID={access_key}\n")
            f.write(f"AWS_SECRET_ACCESS_KEY={secret_key}\n")
        logger.info(f"AWS credentials saved to {env_path}")


# Alternative function-based approach (maintaining backward compatibility)
def save_to_s3(image: str, output_path: str) -> bool:
    """
    Upload an image file to S3 bucket.

    Args:
        image (str): Local path of the image file
        label (str): Label information (unused in current implementation)
        output_path (str): S3 destination key

    Returns:
        bool: True if upload successful, False otherwise
    """
    return S3Uploader().upload_file(image, output_path)

