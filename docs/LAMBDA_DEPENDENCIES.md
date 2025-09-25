# Lambda Dependencies Guide

## 📋 Overview

This document explains the dependency management strategy for AWS Lambda functions in the Bedrock monitoring solution.

## ✅ Current Status: **NO LAMBDA LAYERS NEEDED**

Our Lambda functions are designed to use **only built-in libraries** available in the AWS Lambda Python 3.12 runtime, eliminating the need for Lambda layers or additional packaging.

## 🏗️ Architecture Decision

### Lambda Functions (Cloud Execution)
- **Purpose**: Lightweight metrics collection and alerting
- **Dependencies**: Only AWS Lambda built-in libraries
- **Deployment**: Simple inline code - no layers required

### Python Scripts (Local Execution)  
- **Purpose**: Complex reporting, analytics, and visualization
- **Dependencies**: Full data science stack (pandas, matplotlib, etc.)
- **Deployment**: Local development environment only

## 📦 Dependency Breakdown

### Available by Default in AWS Lambda Python 3.12

| Library | Version | Usage |
|---------|---------|--------|
| `boto3` | Latest | AWS API calls |
| `botocore` | Latest | AWS SDK core |
| `json` | Built-in | JSON processing |
| `os` | Built-in | Environment variables |
| `datetime` | Built-in | Time operations |
| `logging` | Built-in | Logging |
| `typing` | Built-in | Type hints |
| `statistics` | Built-in | Basic math |
| `collections` | Built-in | Data structures |
| `re` | Built-in | Regular expressions |
| `base64` | Built-in | Encoding |
| `io` | Built-in | I/O operations |

### NOT Available (Used Only in Local Scripts)

| Library | Used In | Purpose |
|---------|---------|---------|
| `pandas` | bedrock_reporter.py | Data analysis |
| `matplotlib` | bedrock_reporter.py | Plotting |
| `seaborn` | bedrock_reporter.py | Statistical plots |
| `jinja2` | bedrock_reporter.py | HTML templates |
| `numpy` | Via pandas/matplotlib | Numerical computing |

## 🚀 Benefits of This Approach

### ✅ **Simplified Deployment**
- No Lambda layers to create or maintain
- No package size limits to worry about
- Faster cold starts (smaller function size)
- No layer version compatibility issues

### ✅ **Cost Effective**
- No additional storage costs for layers
- Faster execution (built-in libraries)
- Reduced complexity

### ✅ **Maintenance Free**
- AWS manages all library updates
- No security patching required
- Always latest boto3 version

## 📁 File Structure

```
python-scripts/
├── requirements.txt              # Local development (full stack)
├── requirements-lambda.txt       # Lambda (built-in only)
├── bedrock_monitor.py           # ✅ Lambda compatible
├── enable_bedrock_logging.py    # ✅ Lambda compatible  
├── validate_config.py           # ✅ Lambda compatible
└── bedrock_reporter.py          # ❌ Local only (uses pandas/matplotlib)
```

## 🔄 If You Need Lambda Layers (Future)

If you ever need to add external libraries to Lambda functions, here are your options:

### Option 1: Create Lambda Layer
```bash
# Create layer with pandas/numpy
mkdir python
pip install pandas numpy -t python/
zip -r pandas-layer.zip python/

# Upload to AWS Lambda Layers
aws lambda publish-layer-version \
  --layer-name pandas-numpy-layer \
  --zip-file fileb://pandas-layer.zip \
  --compatible-runtimes python3.12
```

### Option 2: Package with Function
```bash
# Include dependencies with function code
pip install pandas -t ./
zip -r function.zip .
```

### Option 3: Container Images
```dockerfile
FROM public.ecr.aws/lambda/python:3.12
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY lambda_function.py .
CMD ["lambda_function.lambda_handler"]
```

## 🎯 Recommendation

**Keep the current architecture** - it's optimized for performance, cost, and maintainability. The Lambda functions handle lightweight metrics collection while the heavy analytics work is done locally where full library access is available.

## 📊 Current Lambda Functions

| Function | Dependencies | Layer Needed? |
|----------|-------------|---------------|
| `BedrockCustomMetricsLambda` | boto3, json, os, datetime | ❌ No |

All functions use only built-in libraries = **Zero Lambda layers required!**