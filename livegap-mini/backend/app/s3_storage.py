"""S3 storage utilities for video uploads"""
import os
import logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Control whether to delete local videos after S3 upload
# Set to "false" on Windows dev to avoid WinError 32
# Set to "true" on EC2 prod to save disk space
DELETE_LOCAL_VIDEOS = os.getenv("DELETE_LOCAL_VIDEOS", "false").lower() == "true"


def get_s3_client():
    """Get boto3 S3 client. Uses AWS credentials from environment or IAM role."""
    return boto3.client('s3', region_name=os.getenv("AWS_REGION", "us-east-1"))


def upload_video_to_s3(local_path: str, filename: str) -> str | None:
    """
    Upload a video file to S3 and return the CloudFront URL.
    ALWAYS deletes local file after upload to save disk space.
    
    Args:
        local_path: Path to the local .webm file
        filename: Name for the file in S3 (e.g., "abc123.webm")
    
    Returns:
        CloudFront URL if successful, None if upload failed
    """
    bucket = os.getenv("AWS_S3_BUCKET")
    cloudfront_domain = os.getenv("CLOUDFRONT_DOMAIN")
    
    if not bucket:
        print("[S3] ERROR: AWS_S3_BUCKET not configured - S3 upload required!")
        return None
    
    if not cloudfront_domain:
        print("[S3] ERROR: CLOUDFRONT_DOMAIN not configured - S3 upload required!")
        return None
    
    try:
        s3_client = get_s3_client()
        s3_key = f"videos/{filename}"
        
        print(f"[S3] Uploading {local_path} to s3://{bucket}/{s3_key}")
        
        # Upload with public-read ACL or rely on CloudFront OAI/OAC permissions
        s3_client.upload_file(
            local_path,
            bucket,
            s3_key,
            ExtraArgs={
                'ContentType': 'video/webm',
                # Don't set ACL if using OAI/OAC - bucket policy handles access
                # 'ACL': 'public-read'  # Uncomment if NOT using OAI/OAC
            }
        )
        
        # Return CloudFront URL
        cloudfront_url = f"https://{cloudfront_domain}/videos/{filename}"
        print(f"[S3] Upload successful: {cloudfront_url}")
        
        # Delete local file after successful upload (only if enabled)
        if DELETE_LOCAL_VIDEOS:
            try:
                Path(local_path).unlink()
                print(f"[S3] Deleted local file: {local_path}")
            except Exception as e:
                logger.warning(f"[S3] Could not delete local file (will skip): {e}")
        else:
            print(f"[S3] Keeping local file (DELETE_LOCAL_VIDEOS=false): {local_path}")
        
        return cloudfront_url
        
    except ClientError as e:
        print(f"[S3] Upload failed: {e}")
        return None
    except Exception as e:
        print(f"[S3] Unexpected error during upload: {e}")
        return None


__all__ = ["upload_video_to_s3"]
