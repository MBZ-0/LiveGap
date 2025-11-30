#!/usr/bin/env python3
"""Test script to verify S3 access from EC2 with IAM role"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    import boto3
    from botocore.exceptions import ClientError
    from dotenv import load_dotenv
    
    # Load environment variables
    env_path = Path(__file__).parent / "backend" / ".env"
    load_dotenv(env_path)
    
    print("=" * 60)
    print("🔍 S3 Connection Test")
    print("=" * 60)
    
    # Get configuration
    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_REGION", "us-east-1")
    cloudfront = os.getenv("CLOUDFRONT_DOMAIN")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    has_secret = bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    
    print(f"\n📋 Configuration:")
    print(f"   Bucket: {bucket}")
    print(f"   Region: {region}")
    print(f"   CloudFront: {cloudfront}")
    print(f"   Access Key: {access_key[:10]}...{access_key[-4:] if access_key else 'NOT SET'}")
    print(f"   Secret Key: {'✓ SET' if has_secret else '✗ NOT SET'}")
    
    if not bucket or bucket == "your-bucket-name":
        print("\n❌ ERROR: AWS_S3_BUCKET not configured in .env")
        print("   Please update backend/.env with your actual bucket name")
        sys.exit(1)
    
    print(f"\n🔐 Testing IAM Role Authentication...")
    
    # Try to create S3 client (will use IAM role automatically)
    s3 = boto3.client('s3', region_name=region)
    
    # Try to access the bucket
    print(f"\n📦 Testing bucket access: s3://{bucket}/")
    
    try:
        # List objects in videos/ prefix
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix="videos/",
            MaxKeys=5
        )
        
        print(f"✅ Successfully connected to S3!")
        
        if 'Contents' in response:
            print(f"\n📹 Found {len(response['Contents'])} video(s) in videos/ prefix:")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"   - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print(f"\n📂 Bucket accessible, but videos/ folder is empty")
            print(f"   This is normal for a new setup")
        
        # Test upload permission with a tiny test file
        print(f"\n🧪 Testing upload permission...")
        test_key = "videos/test-connection.txt"
        test_content = "S3 connection test successful"
        
        s3.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=test_content.encode(),
            ContentType="text/plain"
        )
        
        print(f"✅ Upload test successful!")
        print(f"   Created: s3://{bucket}/{test_key}")
        
        # Clean up test file
        s3.delete_object(Bucket=bucket, Key=test_key)
        print(f"✅ Cleanup successful (test file deleted)")
        
        print(f"\n🎉 All tests passed!")
        print(f"\n✅ Your EC2 instance can:")
        print(f"   - Authenticate using IAM role")
        print(f"   - Read from S3 bucket")
        print(f"   - Upload to S3 bucket")
        print(f"   - Delete from S3 bucket")
        
        print(f"\n🚀 Ready to upload videos!")
        print(f"   Backend will upload to: s3://{bucket}/videos/")
        print(f"   CloudFront will serve: https://{cloudfront}/videos/")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"\n❌ S3 Access Error: {error_code}")
        
        if error_code == 'NoSuchBucket':
            print(f"\n   Bucket '{bucket}' does not exist!")
            print(f"   Solutions:")
            print(f"   1. Create the bucket in AWS Console")
            print(f"   2. Or update AWS_S3_BUCKET in .env with correct name")
        
        elif error_code == 'AccessDenied':
            print(f"\n   Permission denied!")
            print(f"   Solutions:")
            print(f"   1. Verify IAM role 'another-ai-ec2-role' has S3 permissions")
            print(f"   2. Wait 15-30 seconds for IAM changes to propagate")
            print(f"   3. Check bucket policy allows your account")
        
        else:
            print(f"   Error: {e.response['Error']['Message']}")
        
        sys.exit(1)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print(f"\n   Missing dependencies. Install with:")
    print(f"   pip install boto3 python-dotenv")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
