# save_to_s3.py

import os
from getpass import getpass
from typing import Optional, Dict, Any

import boto3
import botocore.exceptions
from dotenv import load_dotenv
from loguru import logger


# Load environment variables from .env file (if present)
load_dotenv()

class S3Uploader:
    """A class to upload files to Amazon S3 with robust error handling."""

    def __init__(self, region_name: Optional[str] = None, bucket_name: Optional[str] = None):
        """
        Initialize the S3 uploader.

        Args:
            region_name (str): AWS region name. If not provided, uses environment variable.
            bucket_name (str): S3 bucket name. If not provided, uses environment variable.
        """
        # Load from env or defaults
        self.region_name = region_name or os.environ.get("S3_REGION")
        self.bucket_name = bucket_name or os.environ.get("S3_BUCKET_NAME")

        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        # If any required credential is missing, prompt user
        if not all([self.region_name, self.bucket_name, aws_access_key_id, aws_secret_access_key]):
            logger.warning("Missing AWS credentials. Please provide them.")

            # Prompt for input and update instance variables directly
            self.region_name = getpass("Enter AWS Region: ").strip()
            self.bucket_name = getpass("Enter S3 Bucket Name: ").strip()
            aws_access_key_id = getpass("Enter AWS Access Key ID: ").strip()
            aws_secret_access_key = getpass("Enter AWS Secret Access Key: ").strip()

            # Save to .env
            self._save_to_env(self.region_name, self.bucket_name, aws_access_key_id, aws_secret_access_key)

        # Validate required credentials
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError("AWS Access Key ID and Secret Access Key are required.")

        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
            logger.info(f"S3 client initialized for bucket '{self.bucket_name}' in {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a file from the local filesystem to an S3 bucket.

        Args:
            local_path (str): Path to the local file.
            s3_key (str): Key (path) in the S3 bucket where the file will be stored.

        Returns:
            bool: True if upload succeeded, False otherwise.
        """
        try:
            # Validate inputs
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file '{local_path}' does not exist")

            if not s3_key.strip():
                raise ValueError("S3 key cannot be empty or whitespace-only")

            logger.info(f"Uploading {os.path.basename(local_path)} to S3: {s3_key}")

            # Upload the file
            self.s3_client.upload_file(
                Filename=local_path,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.success(f"Successfully uploaded '{local_path}' to s3://{self.bucket_name}/{s3_key}")
            return True

        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"AWS Client Error ({error_code}): {error_message}")
            return False

        except botocore.exceptions.NoCredentialsError:
            logger.error("AWS credentials not found. Please check your environment or input.")
            return False

        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False

    def _save_to_env(self, region_name: str, bucket_name: str, access_key: str, secret_key: str):
        """Save AWS credentials to .env file (optional)."""
        env_path = ".env"
        try:
            # # Check if we already have these values
            # with open(env_path, "r") as f:
            #     existing_content = f.read()
            #     has_region = f"S3_REGION='{region_name}'" in existing_content
            #     has_bucket = f"S3_BUCKET_NAME='{bucket_name}'" in existing_content
            #     has_access_key = f"AWS_ACCESS_KEY_ID='{access_key}'" in existing_content
            #     has_secret_key = f"AWS_SECRET_ACCESS_KEY='{secret_key}'" in existing_content

            # Only write if not already present (avoid duplicates)
            with open(env_path, "a") as f:
                if not has_region:
                    f.write(f"\nS3_REGION='{region_name}'")
                if not has_bucket:
                    f.write(f"\nS3_BUCKET_NAME='{bucket_name}'")
                if not has_access_key:
                    f.write(f"\nAWS_ACCESS_KEY_ID='{access_key}'")
                if not has_secret_key:
                    f.write(f"\nAWS_SECRET_ACCESS_KEY='{secret_key}'")

            logger.info(f"Credentials saved to {env_path}")
        except Exception as e:
            logger.warning(f"Failed to save credentials to .env: {e}")


# Backward-compatible function (for legacy usage)
def save_to_s3(image: str, output_path: str) -> bool:
    """
    Upload an image file to S3.

    Args:
        image (str): Local path of the image.
        output_path (str): S3 key (path).

    Returns:
        bool: True if upload succeeded, False otherwise.
    """
    uploader = S3Uploader()
    return uploader.upload_file(image, output_path)
