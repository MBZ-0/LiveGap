# S3 Video Storage Setup Guide

## Overview
Videos are now uploaded to S3 and served via CloudFront instead of being stored locally.

## Changes Made

### Backend
1. **Added boto3** to `requirements.txt` for AWS S3 SDK
2. **Created `app/s3_storage.py`** - S3 upload utility
3. **Updated `app/agent.py`** - Videos now upload to S3 after recording
4. **Updated `.env`** - Added AWS configuration variables

### Frontend
1. **Updated `page.tsx`** - Video URLs now use CloudFront URLs directly (no `/api` prefix needed)

## AWS Setup Required

### 1. S3 Bucket Configuration

**Create/Configure Bucket:**
```bash
# Your bucket should already exist. Verify it's in the right region.
aws s3 ls s3://your-bucket-name/videos/
```

**Bucket Policy (if using OAI/OAC):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity YOUR-OAI-ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/videos/*"
    }
  ]
}
```

### 2. CloudFront Configuration

**Verify/Create Behavior for `/videos/*`:**
- **Path Pattern:** `/videos/*`
- **Origin:** Your S3 bucket
- **Origin Access:** Use OAI or OAC (recommended)
- **Cache Policy:** CachingOptimized
- **Viewer Protocol Policy:** Redirect HTTP to HTTPS

**Test CloudFront access:**
```bash
# After uploading a test video
curl -I https://d3lcgzvi9bu5xi.cloudfront.net/videos/test.webm
# Should return 200 OK with content-type: video/webm
```

### 3. EC2/Backend IAM Permissions

**Option A: IAM Role (Recommended for EC2)**
Attach this policy to your EC2 instance role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/videos/*"
    }
  ]
}
```

**Option B: Access Keys (Less Secure)**
Set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

### 4. Environment Variables

Update `.env` on your EC2 instance:
```bash
# AWS S3 Configuration for Video Storage
AWS_S3_BUCKET=your-actual-bucket-name  # Replace this!
AWS_REGION=us-east-1
CLOUDFRONT_DOMAIN=d3lcgzvi9bu5xi.cloudfront.net
```

**Important:** Replace `your-bucket-name` with your actual S3 bucket name!

## Deployment Steps

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt  # Installs boto3
```

### 2. Update Environment Variables
```bash
# On EC2 or your deployment environment
nano /path/to/backend/.env
# Update AWS_S3_BUCKET with real bucket name
```

### 3. Verify IAM Permissions
```bash
# Test S3 upload from EC2
aws s3 cp test.txt s3://your-bucket-name/videos/test.txt
# Should succeed without errors
```

### 4. Deploy Backend
```bash
# Restart your backend service
sudo systemctl restart your-backend-service
# Or if using uvicorn directly:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Deploy Frontend
```bash
cd frontend
npm run build
# Deploy the out/ folder to your hosting
```

## Verification

### Test Video Upload
1. Run a reality check test
2. Check backend logs for:
   ```
   [S3] Uploading /path/to/video.webm to s3://bucket/videos/abc123.webm
   [S3] Upload successful: https://d3lcgzvi9bu5xi.cloudfront.net/videos/abc123.webm
   ```
3. Verify video appears in S3:
   ```bash
   aws s3 ls s3://your-bucket-name/videos/
   ```
4. Test CloudFront URL in browser:
   ```
   https://d3lcgzvi9bu5xi.cloudfront.net/videos/abc123.webm
   ```

## Fallback Behavior

If S3 upload fails:
- Video URL falls back to `/videos/filename.webm` (local path)
- Check logs for upload errors
- Verify IAM permissions and bucket configuration

## Troubleshooting

### "Access Denied" Errors
- **Check IAM role/policy** on EC2 instance
- **Verify bucket policy** allows OAI/OAC access
- **Check bucket exists** and is in correct region

### CloudFront 403 Errors
- **Verify CloudFront distribution** has correct origin
- **Check OAI/OAC** is properly configured
- **Test direct S3 URL** (if allowed) to isolate issue

### Videos Not Appearing
- **Check backend logs** for upload success/failure
- **Verify S3 bucket** contains uploaded files
- **Test CloudFront URL** directly in browser
- **Check CORS** if accessing from different domain

## Cost Considerations

- **S3 Storage:** ~$0.023/GB/month (Standard)
- **S3 PUT Requests:** $0.005 per 1,000 requests
- **CloudFront Data Transfer:** First 10 TB/month ~$0.085/GB
- **Estimated cost:** ~$5-10/month for moderate usage (100 videos/month)

## Local Development

For local development, S3 upload is **optional**:
- If `AWS_S3_BUCKET` is not set, videos stay local at `/videos/*`
- Backend serves videos from `app/videos/` directory
- Frontend works with both local and CloudFront URLs

## Security Notes

1. **Never commit AWS credentials** to git
2. **Use IAM roles** instead of access keys when possible
3. **Restrict bucket policy** to specific CloudFront OAI/OAC
4. **Enable CloudFront logging** for audit trails
5. **Consider bucket versioning** for video recovery
