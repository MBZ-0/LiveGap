# another.ai

> **See how badly your AI agent fails on real websites.**

An AI-powered web agent testing platform that evaluates how well automated browser agents navigate real-world SaaS websites. Watch your agent attempt common tasks like finding pricing, contacting sales, or signing up — and see where it succeeds or fails.

[![CI Status](https://github.com/MBZ-0/LiveGap/actions/workflows/ci.yml/badge.svg)](https://github.com/MBZ-0/LiveGap/actions)

**🌐 Live Production App:** [https://d3lcgzvi9bu5xi.cloudfront.net](https://d3lcgzvi9bu5xi.cloudfront.net)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Live Demo Access](#-live-demo-access)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start (Local Development)](#-quick-start-local-development)
- [Production Deployment](#-production-deployment)
- [Environment Configuration](#-environment-configuration)
- [Testing & CI/CD](#-testing--cicd)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## 🎯 Overview

**another.ai** is a full-stack web application that stress-tests AI agents against real websites. It uses:

- **LLM-driven planning** (OpenAI GPT-4o-mini) for intelligent navigation
- **Playwright** for headless browser automation
- **Video recording** of every agent session
- **Declarative success criteria** via YAML configuration
- **Real-time progress tracking** with background job processing

### How It Works

1. User selects a goal (e.g., "Find pricing information")
2. Agent tests 10 major SaaS platforms simultaneously
3. For each site, the agent:
   - Loads the page in Chromium
   - Uses LLM to plan actions (click, scroll, type)
   - Records video of the entire session
   - Validates success against configured URLs
   - Generates detailed markdown report
4. Results displayed with success rate, videos, and step-by-step analysis

### Supported Goals

| Goal | Description |
|------|-------------|
| **Talk to Sales** | Reach sales team, request demo |
| **Pricing** | Locate pricing/plans information |
| **Sign Up** | Create account or get started |
| **Help** | Find documentation/support |
| **Customers** | View customer stories/testimonials |

### Tested Platforms

- Intercom, HubSpot, Asana, Calendly, Notion
- Airtable, Zendesk, Atlassian, Monday.com, Slack

---

## 🌐 Live Demo Access

**🚀 Production URL:** [https://d3lcgzvi9bu5xi.cloudfront.net](https://d3lcgzvi9bu5xi.cloudfront.net)

**No login required** — the application is publicly accessible.

### Quick Demo Steps

1. Visit the production URL
2. Click **"New"** button to create a test
3. Enter a test name (e.g., "Pricing Test")
4. Select a goal from the dropdown
5. Click **"Run test on 10 SaaS sites"**
6. Watch real-time progress (updates every 3 seconds)
7. Click **"Video"** or **"Report"** buttons to see results

### Example Test

```
Test Name: Sales Contact Test
Goal: I'm trying to talk to sales — can you help me reach the sales team?
Expected Duration: 30-60 seconds
Expected Success Rate: 40-70%
```

---

## ✨ Features

### Core Capabilities

- ✅ **LLM-Driven Agent** — GPT-4o-mini plans each action intelligently
- ✅ **Multi-Site Testing** — Tests 10 platforms in parallel (max 3 concurrent)
- ✅ **Video Recording** — Every session recorded in 1280x900 resolution
- ✅ **Cloud Storage** — Videos stored in S3, served via CloudFront CDN
- ✅ **Real-Time Updates** — Frontend polls for status every 3 seconds
- ✅ **Detailed Reports** — Markdown-formatted step-by-step analysis
- ✅ **Declarative Config** — Sites/success criteria in YAML (no code changes)
- ✅ **Background Jobs** — Non-blocking API with job queue
- ✅ **Responsive UI** — Dark theme, accessible components

### Technical Highlights

- **Backend:** FastAPI (Python) with async/await
- **Frontend:** Next.js 14 with TypeScript
- **Browser:** Playwright Chromium automation
- **AI:** OpenAI GPT-4o-mini for decision-making
- **Storage:** AWS S3 + CloudFront for video delivery
- **Testing:** 85% backend coverage (pytest), 70% frontend coverage (Jest)
- **CI/CD:** GitHub Actions for automated testing

---

## 🏗️ Architecture

![Architecture Diagram](./architecture-diagram.png)

### Architecture Components

| Architecture Component                           | Code / Docs Location                                   | One-Sentence Integration Description |
|--------------------------------------------------|--------------------------------------------------------|--------------------------------------|
| **User Browser (Next.js UI)**                    | [`livegap-mini/frontend/app/page.tsx`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/frontend/app/page.tsx) | Renders the main dashboard UI and sends HTTPS requests to CloudFront for static assets and `/api/*` calls. |
| **AWS CloudFront (Public CDN Endpoint)**         | [`README.md`](https://github.com/MBZ-0/LiveGap/blob/main/README.md) – *Architecture / Production Deployment* | Acts as the single public entrypoint, serving the static Next.js frontend from S3 and proxying `/api/*` requests to the EC2 backend. |
| **S3 Frontend Bucket (Next.js Export)**          | `livegap-mini/frontend` build output (`out/`)         | Hosts the exported static Next.js site that CloudFront serves to users. |
| **EC2 Backend (FastAPI)**                        | [`livegap-mini/backend/app/main.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/main.py) | Exposes the REST API (`/api/run-reality-check`, `/api/run/{run_id}`) and orchestrates agent runs for each request. |
| **Playwright Browser (Headless Chromium)**       | [`livegap-mini/backend/app/agent.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/agent.py) & [`runner.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/runner.py) | Runs headless Chromium sessions on EC2 to execute the reference browser agent across the 10 SaaS sites. |
| **Local Video File (Temporary)**                 | `livegap-mini/backend/app/videos/` (via [`agent.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/agent.py)) | Stores raw session recordings on disk before they are uploaded to the S3 video bucket. |
| **S3 Video Bucket (Recordings)**                 | [`livegap-mini/backend/app/s3_storage.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/s3_storage.py) | Receives uploaded `.webm` recordings from the backend and serves them via CloudFront `/videos/*` URLs for playback in the UI. |
| **OpenAI API (LLM Requests)**                    | [`livegap-mini/backend/app/llm.py`](https://github.com/MBZ-0/LiveGap/blob/main/livegap-mini/backend/app/llm.py) | Sends LLM requests from the EC2 backend to OpenAI to power agent reasoning and generate human-readable reports. |

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14, React 18, TypeScript | Server-rendered UI |
| **Backend** | FastAPI, Python 3.11 | RESTful API |
| **Browser** | Playwright Chromium | Headless automation |
| **AI** | OpenAI GPT-4o-mini | Action planning |
| **Storage** | AWS S3 + CloudFront | Video CDN |
| **Deployment** | EC2 (Ubuntu) + S3 Static Hosting | Production infra |
| **CI/CD** | GitHub Actions | Automated testing |

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Node.js 18+** (20 recommended)
- **Git**
- **OpenAI API Key** (for LLM planning)

### Step 1: Clone Repository

```powershell
git clone https://github.com/MBZ-0/LiveGap.git
cd LiveGap
```

### Step 2: Backend Setup

```powershell
# Navigate to backend
cd livegap-mini/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
python -m playwright install chromium

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

# Optional: Add AWS credentials for video upload (not required for local dev)
# echo "AWS_S3_BUCKET=your-bucket" >> .env
# echo "CLOUDFRONT_DOMAIN=your-domain.cloudfront.net" >> .env
# echo "AWS_REGION=us-east-1" >> .env
```

### Step 3: Run Backend Server

```powershell
# From livegap-mini/backend directory
python run_dev.py
# Or:
uvicorn app.main:app --reload --port 8000
```

**Backend running at:** `http://localhost:8000`

**Health check:** `http://localhost:8000/health`

### Step 4: Frontend Setup

Open a **new terminal** window:

```powershell
# Navigate to frontend
cd livegap-mini/frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000/api" > .env.local

# Run development server
npm run dev
```

**Frontend running at:** `http://localhost:3000`

### Step 5: Test the Application

1. Open browser to `http://localhost:3000`
2. Click **"New"** button
3. Enter test name and select a goal
4. Click **"Run test on 10 SaaS sites"**
5. Watch results appear in real-time

**Note:** Without S3 credentials, videos won't be uploaded (this is OK for local testing — you'll still see agent execution and reports).

---

## 📦 Production Deployment

### Current Production Setup

**Live URL:** [https://d3lcgzvi9bu5xi.cloudfront.net](https://d3lcgzvi9bu5xi.cloudfront.net)

Our production deployment uses:
- **Frontend:** S3 Static Website Hosting
- **Backend:** EC2 Instance (Ubuntu, t2.micro)
- **CDN:** CloudFront Distribution
- **Storage:** S3 Bucket for videos
- **Region:** us-east-1

### Deployment Steps for Teammates

#### 1️⃣ Backend Deployment (EC2)

**Step 1:** Launch EC2 Instance

```bash
# Instance specifications:
AMI: Ubuntu Server 22.04 LTS
Instance Type: t2.small or larger (Chromium requires memory)
Storage: 20 GB minimum
Security Group: Allow inbound TCP 8000 (or custom port)
```

**Step 2:** Connect to EC2 and Install Dependencies

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install system dependencies for Playwright
sudo apt install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 \
  libasound2 libpangocairo-1.0-0 libgtk-3-0

# Install Git
sudo apt install git -y
```

**Step 3:** Clone and Setup Application

```bash
# Clone repository
git clone https://github.com/MBZ-0/LiveGap.git
cd LiveGap/livegap-mini/backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
python -m playwright install chromium
```

**Step 4:** Configure Environment Variables

```bash
# Create .env file
nano .env

# Add these variables:
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
AWS_S3_BUCKET=another-ai-videos
CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net
AWS_REGION=us-east-1
DELETE_LOCAL_VIDEOS=true
MAX_CONCURRENT_SITES=3
AGENT_MAX_SECONDS=30
LLM_MAX_STEPS=8

# Save and exit (Ctrl+O, Enter, Ctrl+X)
```

**Step 5:** Setup AWS Credentials (IAM Role or Access Keys)

**Option A: IAM Role (Recommended)**

```bash
# Attach IAM role to EC2 instance with S3 permissions:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::another-ai-videos/*"
    }
  ]
}
```

**Option B: Access Keys (Alternative)**

```bash
# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: us-east-1 (region)
# Enter: json (output format)
```

**Step 6:** Run Backend with PM2 (Process Manager)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name another-ai-backend

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it outputs

# Check status
pm2 status
pm2 logs another-ai-backend
```

**Step 7:** Verify Backend is Running

```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

#### 2️⃣ Frontend Deployment (S3 + CloudFront)

**Step 1:** Build Frontend

```bash
# On your local machine (or build server)
cd livegap-mini/frontend

# Install dependencies
npm install

# Create production .env file
echo "NEXT_PUBLIC_API_BASE=https://your-cloudfront-domain.cloudfront.net/api" > .env.production

# Build for production
npm run build

# Export static files
# (Next.js creates an 'out' directory with static HTML/JS/CSS)
```

**Step 2:** Create S3 Bucket for Frontend

```bash
# Create bucket (via AWS Console or CLI)
aws s3 mb s3://another-ai-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://another-ai-frontend --index-document index.html

# Upload build files
aws s3 sync out/ s3://another-ai-frontend/ --delete

# Set public read permissions (or use CloudFront OAI)
aws s3api put-bucket-policy --bucket another-ai-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::another-ai-frontend/*"
  }]
}'
```

**Step 3:** Create S3 Bucket for Videos

```bash
# Create video storage bucket
aws s3 mb s3://another-ai-videos --region us-east-1

# Block public access (CloudFront will access via OAI)
aws s3api put-public-access-block --bucket another-ai-videos --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

**Step 4:** Setup CloudFront Distribution

```bash
# Via AWS Console:
1. Go to CloudFront → Create Distribution
2. Origin Domain: another-ai-frontend.s3-website-us-east-1.amazonaws.com
3. Add second origin: EC2 public DNS (for /api/*)
4. Behaviors:
   - /* → S3 origin (frontend)
   - /api/* → EC2 origin (backend)
5. Add third origin: another-ai-videos.s3.us-east-1.amazonaws.com
6. Add behavior: /videos/* → S3 videos origin
7. Enable HTTPS (use ACM certificate or CloudFront default)
8. Create distribution
9. Note the CloudFront domain (e.g., d3fxzs3c0qftlv.cloudfront.net)
```

**Step 5:** Update Backend Environment

```bash
# SSH back to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update .env with CloudFront domain
cd LiveGap/livegap-mini/backend
nano .env

# Update this line:
CLOUDFRONT_DOMAIN=d3lcgzvi9bu5xi.cloudfront.net

# Restart backend
pm2 restart another-ai-backend
```

**Step 6:** Test Production Deployment

```bash
# Visit CloudFront URL in browser
https://your-cloudfront-domain.cloudfront.net

# Test backend health check
curl https://your-cloudfront-domain.cloudfront.net/api/health
```

#### 3️⃣ Continuous Deployment (Optional)

**Setup GitHub Actions for Auto-Deploy:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd LiveGap/livegap-mini/backend
            git pull origin main
            source .venv/bin/activate
            pip install -r requirements.txt
            pm2 restart another-ai-backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Build and Deploy
        run: |
          cd livegap-mini/frontend
          npm install
          npm run build
          aws s3 sync out/ s3://another-ai-frontend/ --delete
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## ⚙️ Environment Configuration

### Backend Environment Variables

Create `livegap-mini/backend/.env`:

```bash
# Required
OPENAI_API_KEY=sk-proj-...           # OpenAI API key
AWS_S3_BUCKET=another-ai-videos      # S3 bucket for videos
CLOUDFRONT_DOMAIN=d123.cloudfront.net # CloudFront domain
AWS_REGION=us-east-1                 # AWS region

# Optional (with defaults)
OPENAI_MODEL=gpt-4o-mini             # LLM model
OPENAI_ENDPOINT=https://api.openai.com/v1/chat/completions
LLM_MAX_STEPS=8                      # Max planning steps per site
AGENT_MAX_SECONDS=30                 # Timeout per site (seconds)
AGENT_NAV_TIMEOUT=15000              # Page load timeout (ms)
MAX_CONCURRENT_SITES=3               # Parallel site processing
MAX_SITES=10                         # Total sites to test (0=all)
DELETE_LOCAL_VIDEOS=false            # Delete after S3 upload (true in prod)
```

### Frontend Environment Variables

Create `livegap-mini/frontend/.env.local` (development):

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

Create `livegap-mini/frontend/.env.production` (production):

```bash
NEXT_PUBLIC_API_BASE=https://d3lcgzvi9bu5xi.cloudfront.net/api
```

### AWS Credentials

**Production (EC2):** Use IAM Role attached to instance

**Local Development:** Use AWS CLI configuration:

```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

---

## 🧪 Testing & CI/CD

### Local Testing

**Run All Tests:**

```powershell
# From project root
.\run-tests.ps1
```

**Backend Tests Only:**

```powershell
cd livegap-mini\backend
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v

# View coverage report
start htmlcov\index.html
```

**Frontend Tests Only:**

```powershell
cd livegap-mini\frontend
npm run test:coverage

# View coverage report
start coverage\lcov-report\index.html
```

### Test Coverage

- **Backend:** 85% coverage with 45 passing tests
  - Key modules: `agent.py`, `llm.py`, `main.py`, `runner.py` all above 80%
- **Frontend:** 70% statements, 83.8% branches, 97.6% functions
  - Jest + React Testing Library
- **CI Pipeline:** Automated via GitHub Actions

### CI/CD Pipeline

**GitHub Actions Workflow:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

**Jobs:**
1. **Backend Tests** — pytest with coverage on Python 3.11
2. **Frontend Tests** — Jest with coverage on Node.js 20

**View CI Results:** [GitHub Actions](https://github.com/MBZ-0/LiveGap/actions)

### Manual Test Commands

```bash
# Test backend health
curl http://localhost:8000/health

# Test API endpoint
curl -X POST http://localhost:8000/api/run-reality-check \
  -H "Content-Type: application/json" \
  -d '{"goal":"Can you show me the pricing or plans for this company?"}'

# Check Playwright installation
python -m playwright doctor
```

---

## 📚 API Documentation

### Endpoints

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `POST /api/run-reality-check`

Start a new agent test run (non-blocking).

**Request Body:**
```json
{
  "goal": "Can you show me the pricing or plans for this company?"
}
```

**Response:**
```json
{
  "run_id": "abc-123-def-456",
  "status": "pending",
  "created_at": "2025-11-30T12:34:56.789Z"
}
```

#### `GET /api/run/{run_id}`

Get status and results of a test run.

**Response (Pending):**
```json
{
  "run_id": "abc-123",
  "status": "pending",
  "created_at": "2025-11-30T12:34:56.789Z"
}
```

**Response (Running):**
```json
{
  "run_id": "abc-123",
  "status": "running",
  "created_at": "2025-11-30T12:34:56.789Z"
}
```

**Response (Complete):**
```json
{
  "run_id": "abc-123",
  "status": "done",
  "created_at": "2025-11-30T12:34:56.789Z",
  "result": {
    "goal": "Pricing",
    "overall_success_rate": 60.0,
    "total_sites": 10,
    "successful_sites": 6,
    "failed_sites": 4,
    "results": [
      {
        "site_id": "intercom",
        "site_name": "Intercom",
        "url": "https://www.intercom.com/suite",
        "success": true,
        "reason": "https://www.intercom.com/pricing",
        "video_url": "https://d123.cloudfront.net/videos/abc.webm",
        "report": "# Intercom — Goal: Pricing\n..."
      }
    ]
  }
}
```

#### `GET /api/runs`

List all test runs (for debugging).

**Response:**
```json
{
  "runs": [
    {
      "run_id": "abc-123",
      "status": "done",
      "created_at": "2025-11-30T12:34:56.789Z"
    }
  ]
}
```

### Goal Enum Values

```
"I'm trying to talk to sales — can you help me reach the sales team?"
"Can you show me the pricing or plans for this company?"
"How do I create an account or get started?"
"Where can I find documentation or help resources?"
"Can you show me what customers say about this product?"
```

---

## 🔧 Troubleshooting

### Common Issues

#### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
# Ensure virtual environment is activated
cd livegap-mini\backend
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

#### Playwright browser not found

**Error:** `Executable doesn't exist at ...`

**Solution:**
```powershell
python -m playwright install chromium
python -m playwright doctor  # Verify installation
```

#### Windows asyncio error

**Error:** `NotImplementedError: Subprocess is not supported`

**Solution:** Already fixed in `main.py` with:
```python
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

If still occurring, use `python run_dev.py` instead of `uvicorn` directly.

#### Videos not uploading to S3

**Error:** `S3 upload failed: ...`

**Solution:**
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Verify bucket exists
aws s3 ls s3://another-ai-videos/

# Check .env file
cat .env  # Should have AWS_S3_BUCKET, CLOUDFRONT_DOMAIN, AWS_REGION
```

#### Frontend can't connect to backend

**Error:** `Failed to fetch` in browser console

**Solution:**
```powershell
# Check .env.local file
cat livegap-mini\frontend\.env.local
# Should contain: NEXT_PUBLIC_API_BASE=http://localhost:8000/api

# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in backend main.py
```

#### Agent timing out on all sites

**Error:** All sites showing "Time limit reached"

**Solution:**
```bash
# Increase timeout in .env
AGENT_MAX_SECONDS=60
LLM_MAX_STEPS=12

# Check internet connectivity
curl https://www.intercom.com/suite

# Verify Chromium installation
python -m playwright doctor
```

#### OpenAI API errors

**Error:** `No OPENAI_API_KEY present`

**Solution:**
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-proj-..." >> .env

# Verify key works
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Debug Mode

Enable verbose logging:

```bash
# Backend
export PYTHONUNBUFFERED=1
uvicorn app.main:app --reload --port 8000 --log-level debug

# Frontend
npm run dev -- --debug
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check Playwright
python -m playwright doctor

# Check Python version
python --version  # Should be 3.10+

# Check Node version
node --version  # Should be 18+

# Check AWS CLI
aws --version
aws sts get-caller-identity
```

---

## 📁 Project Structure

```
LiveGap/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
├── livegap-mini/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI app + routes
│   │   │   ├── agent.py          # LLM-driven agent logic
│   │   │   ├── llm.py            # OpenAI integration
│   │   │   ├── models.py         # Pydantic schemas
│   │   │   ├── runner.py         # Site loader + config
│   │   │   ├── runs_store.py     # In-memory job storage
│   │   │   ├── s3_storage.py     # S3 upload utilities
│   │   │   ├── success_config.py # Success URL loader
│   │   │   ├── url_matcher.py    # URL normalization
│   │   │   └── videos/           # Temporary video storage
│   │   ├── config/
│   │   │   └── sites.yaml        # Site definitions + success URLs
│   │   ├── tests/                # 45 pytest test files
│   │   ├── requirements.txt      # Python dependencies
│   │   ├── pyproject.toml        # Pytest configuration
│   │   ├── Dockerfile            # Docker image (optional)
│   │   └── run_dev.py            # Development server script
│   ├── frontend/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main dashboard
│   │   │   ├── layout.tsx        # Root layout
│   │   │   ├── globals.css       # Global styles
│   │   │   └── about/            # About page
│   │   ├── components/
│   │   │   └── ui/               # Reusable UI components
│   │   ├── lib/
│   │   │   └── utils.ts          # Utility functions
│   │   ├── coverage/             # Test coverage reports
│   │   ├── package.json          # Node dependencies
│   │   ├── tsconfig.json         # TypeScript config
│   │   ├── tailwind.config.js    # Tailwind CSS config
│   │   ├── jest.config.js        # Jest test config
│   │   └── next.config.mjs       # Next.js config
│   └── S3_SETUP.md              # S3 configuration guide
├── README.md                     # This file
├── CI_SETUP.md                   # Testing documentation
├── SUBMISSION_CHECKLIST.md       # Assignment guide
├── SUMMARY.md                    # CI implementation summary
└── run-tests.ps1                 # Test runner script
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and test**
   ```bash
   .\run-tests.ps1  # Run all tests
   ```
4. **Commit with descriptive message**
   ```bash
   git commit -m "feat: add new feature"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**

### Code Style

- **Python:** Follow PEP 8 (enforced by tests)
- **TypeScript:** Follow Next.js conventions
- **Commits:** Use conventional commit format

### Adding New Test Sites

1. Edit `livegap-mini/backend/config/sites.yaml`
2. Add new site entry:
   ```yaml
   - id: "newsite"
     name: "New Site"
     start_url: "https://newsite.com"
     success:
       pricing:
         - "https://newsite.com/pricing"
       sign_up:
         - "https://newsite.com/signup"
   ```
3. Restart backend
4. Test with `curl` or UI

---

**Built with ❤️ for CSC 454/491 — Fall 2025***
