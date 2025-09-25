# AWS Bedrock Enhanced Monitoring & Logging Solution

[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)
[![CloudFormation](https://img.shields.io/badge/Infrastructure-CloudFormation-blue)](https://aws.amazon.com/cloudformation/)
[![Python](https://img.shields.io/badge/Analytics-Python-green)](https://www.python.org/)
[![Monitoring](https://img.shields.io/badge/Monitoring-CloudWatch-yellow)](https://aws.amazon.com/cloudwatch/)
[![Logging](https://img.shields.io/badge/Logging-Enhanced-purple)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Enhanced Logging Features](#enhanced-logging-features)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Dashboard Overview](#dashboard-overview)
- [Custom Metrics](#custom-metrics)
- [Alerting](#alerting)
- [Reporting](#reporting)
- [Security Considerations](#security-considerations)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This enhanced monitoring solution for AWS Bedrock provides enterprise-grade observability, security auditing, and cost management capabilities with **triple-layer logging integration**. Designed following AWS Well-Architected Framework principles, it enables organizations to:

- **Monitor** Bedrock service usage patterns and performance
- **Audit** user behavior and security events with CloudTrail
- **Log** model invocations natively with Bedrock's built-in logging
- **Track** detailed metrics through CloudWatch integration
- **Optimize** costs through detailed usage analytics
- **Alert** on anomalies and performance issues
- **Report** to stakeholders with automated insights

### 🔍 Triple-Layer Logging Architecture

This solution implements a comprehensive three-tier logging strategy:

1. **📋 CloudTrail Logging** - API-level audit trails for security and compliance
2. **📊 CloudWatch Logging** - Performance metrics and operational insights
3. **🎯 Bedrock Native Logging** - Model invocation details with request/response payloads

### 🏗️ Solution Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Infrastructure** | Core monitoring setup | CloudFormation |
| **Native Logging** | Bedrock model invocation logs | Bedrock Model Invocation Logging |
| **API Logging** | Security & compliance auditing | CloudTrail |
| **Operational Monitoring** | Performance & metrics | CloudWatch |
| **Dashboards** | Multi-stakeholder views | CloudWatch Dashboards |
| **Analytics** | Custom metrics & insights | Python + Lambda |
| **Alerting** | Proactive notifications | SNS + CloudWatch Alarms |
| **Reporting** | Automated documentation | Python + SES |
| **Storage** | Log retention & analysis | S3 + CloudWatch Logs |

## 🏛️ Architecture

![Architecture Diagram](docs/bedrock_monitoring_architecture.png)

### Architecture Layers

1. **Application Layer**: Web apps, mobile apps, and API clients
2. **Bedrock Services**: Runtime API and Foundation Models
3. **Monitoring Infrastructure**: CloudTrail, CloudWatch, Lambda functions
4. **Storage Layer**: S3 buckets and CloudWatch Log Groups
5. **Analytics & Reporting**: Custom analytics and automated reporting
6. **Dashboard Layer**: Technical, Management, Security, and Cost dashboards

### Data Flow

![Data Flow Diagram](docs/bedrock_data_flow.png)

The solution processes data through multiple stages:

- **Real-time**: API calls, metrics, alerts (< 5 minutes)
- **Near real-time**: Log aggregation, processing (5-15 minutes)
- **Batch**: Daily/weekly reports, trend analysis

## 🔍 Enhanced Logging Features

### 🎯 Bedrock Native Model Invocation Logging

This solution includes comprehensive **Bedrock Model Invocation Logging** that captures detailed request and response data:

**What Gets Logged:**

- ✅ **Model Invocations**: Every call to Bedrock foundation models
- ✅ **Request Payloads**: Input prompts, parameters, and configurations
- ✅ **Response Payloads**: Generated text, tokens used, and metadata
- ✅ **Performance Metrics**: Latency, throughput, and processing times
- ✅ **Error Details**: Failed requests with detailed error messages
- ✅ **User Context**: Identity, session, and application information

**Logging Destinations:**

- **CloudWatch Logs**: Real-time log streaming and analysis
- **S3 Bucket**: Long-term storage and compliance archiving
- **Custom Analytics**: Python-based processing and insights

**Key Benefits:**

- 🔍 **Deep Visibility**: See exactly what prompts and responses are being processed
- 🛡️ **Security Monitoring**: Track sensitive data usage and potential leaks
- 📊 **Usage Analytics**: Understand how models are being utilized
- 💰 **Cost Attribution**: Precise token usage tracking per user/application
- 🚨 **Anomaly Detection**: Identify unusual patterns in model usage

### 📋 CloudTrail Integration

Comprehensive API-level logging for security and compliance:

- All Bedrock API calls (InvokeModel, ListFoundationModels, etc.)
- Administrative actions (CreateModel, UpdateModel, etc.)
- User authentication and authorization events
- Cross-service interactions and dependencies

### 📊 CloudWatch Metrics & Logs

Operational monitoring and performance insights:

- Real-time metrics dashboards and custom alarms
- Log aggregation from Lambda functions and applications
- Performance monitoring and threshold-based alerting
- Integration with AWS X-Ray for distributed tracing

## ✨ Key Features

### 🔍 Comprehensive Monitoring

- **API Usage Tracking**: All Bedrock API calls with detailed metrics
- **Performance Monitoring**: Response times, throughput, error rates
- **Token Usage Analytics**: Input/output token consumption by model
- **User Behavior Analysis**: Access patterns and usage trends
- **Cost Tracking**: Real-time cost estimation and optimization insights

### 🛡️ Security & Compliance

- **CloudTrail Integration**: Complete audit trail of all API activities
- **Access Monitoring**: User authentication and authorization tracking
- **Anomaly Detection**: Unusual usage patterns and security events
- **IP Address Tracking**: External access attempts and geolocation
- **Compliance Reporting**: SOC, PCI, HIPAA-ready audit logs

### 📊 Multi-Stakeholder Dashboards

- **Technical Operations**: Performance metrics, error analysis, system health
- **Management**: KPIs, trends, ROI analysis, executive summaries
- **Security**: Access patterns, threat detection, compliance status
- **Finance**: Cost analysis, budget tracking, usage optimization

### 🤖 Intelligent Alerting

- **Threshold-based Alerts**: Custom thresholds for all metrics
- **Anomaly Detection**: ML-powered unusual pattern identification
- **Multi-channel Notifications**: Email, SMS, Slack integration
- **Escalation Policies**: Tiered response for critical issues
- **Alert Correlation**: Reduce noise through intelligent grouping

### 📈 Automated Reporting

- **Daily Summaries**: Usage, performance, and cost reports
- **Weekly Trends**: Analysis of patterns and recommendations
- **Monthly Executive Reports**: High-level insights for leadership
- **Custom Reports**: Tailored analytics for specific stakeholders
- **Compliance Reports**: Automated audit trail documentation

## 📋 Prerequisites

### AWS Account Requirements

- AWS CLI installed and configured
- Appropriate IAM permissions for CloudFormation, CloudWatch, CloudTrail, S3, Lambda, SNS, SES
- Verified email address for SES (for reporting)

### Technical Requirements

- Python 3.10 or higher
- Git
- Bash shell (for deployment scripts)
- jq (JSON processor)

### Minimum IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "cloudwatch:*",
        "logs:*",
        "cloudtrail:*",
        "s3:*",
        "lambda:*",
        "sns:*",
        "ses:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "bedrock:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd bedrock-monitoring-system
```

### 2. Configure Parameters

```bash
# Edit parameters file
vim cloudformation/parameters.json

# Update with your settings:
{
  "Environment": "prod",
  "AlertEmail": "your-email@company.com",
  "CloudTrailRetentionDays": "90",
  "CloudWatchLogRetentionDays": "30"
}
```

### 3. Deploy Infrastructure

```bash
cd cloudformation
chmod +x deploy.sh
./deploy.sh deploy
```

### 4. Access Dashboards

The deployment will output dashboard URLs. Access them from the AWS CloudWatch console.

## 🔧 Detailed Setup

### Step 1: Infrastructure Deployment

**Deploy Core Infrastructure:**

```bash
aws cloudformation deploy \
  --template-file cloudformation/bedrock-monitoring-infrastructure.yaml \
  --stack-name bedrock-monitoring-infrastructure \
  --parameter-overrides file://cloudformation/parameters.json \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region us-east-1
```

**Deploy Dashboards:**

```bash
aws cloudformation deploy \
  --template-file cloudformation/bedrock-monitoring-dashboards.yaml \
  --stack-name bedrock-monitoring-dashboards \
  --parameter-overrides Environment=prod \
  --region us-east-1
```

### Step 2: Enable Bedrock Native Logging

**Automatic Enablement via CloudFormation:**

The infrastructure deployment automatically configures:

- Bedrock Model Invocation Logging Configuration
- CloudWatch Log Group for Bedrock logs
- S3 bucket for long-term log storage
- IAM roles with necessary permissions

**Manual Verification & Configuration:**

```bash
cd python-scripts
python enable_bedrock_logging.py --enable
```

This script will:

- ✅ Verify Bedrock logging configuration
- ✅ Enable model invocation logging if not already active
- ✅ Configure log destinations (CloudWatch + S3)
- ✅ Test logging functionality

### Step 3: Python Environment Setup

**Install Dependencies:**

```bash
cd python-scripts
pip install -r requirements.txt
```

**Configure Environment Variables:**

```bash
export AWS_REGION=us-east-1
export ENVIRONMENT=prod
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:bedrock-monitoring-alerts-prod
export REPORT_BUCKET=bedrock-monitoring-reports-prod
export SENDER_EMAIL=noreply@yourcompany.com
```

### Step 4: Lambda Dependencies

#### ✅ **No Lambda Layers Required!**

Our Lambda functions are optimized to use **only built-in libraries** available in AWS Lambda Python 3.12 runtime:

**Available by default:**

- `boto3` & `botocore` (AWS SDK)
- `json`, `os`, `datetime`, `logging`
- `typing`, `statistics`, `collections`

**Dependency Strategy:**

- **Lambda functions**: Lightweight, built-in libraries only
- **Local scripts**: Full data science stack (pandas, matplotlib, etc.)

For complete details, see: [`docs/LAMBDA_DEPENDENCIES.md`](docs/LAMBDA_DEPENDENCIES.md)

### Step 5: Lambda Function Deployment

**Package and Deploy Custom Metrics Lambda:**

```bash
# Create deployment package
zip -r bedrock-monitor.zip bedrock_monitor.py

# Update Lambda function
aws lambda update-function-code \
  --function-name bedrock-custom-metrics-prod \
  --zip-file fileb://bedrock-monitor.zip
```

## 📊 Dashboard Overview

### 1. Technical Operations Dashboard

**Purpose**: Real-time monitoring for DevOps and SRE teams

**Key Widgets:**

- API Calls Overview (Success/Error/Throttle rates)
- Response Time Distribution
- Token Usage by Model
- Error Analysis and Troubleshooting
- System Health Indicators

**Target Audience:**

- DevOps engineers
- Site reliability engineers
- Platform engineers
- Incident response and troubleshooting

### 2. Management Dashboard

**Purpose**: Business metrics and KPIs for leadership

**Key Widgets:**

- Daily API Usage Trends
- Cost Analysis and Forecasting
- User Adoption Metrics
- Performance vs. SLA Tracking
- ROI and Business Impact Analysis

**Target Audience:**

- Engineering managers
- Product managers
- Business stakeholders
- Executive leadership
- Business performance tracking

### 3. Security Monitoring Dashboard

**Purpose**: Security posture and threat detection

**Key Widgets:**

- External IP Access Attempts
- Authentication Failures
- Unusual Usage Patterns
- Guardrail Violations
- Compliance Status Overview

**Target Audience:**

- Security operations center (SOC)
- Compliance teams
- Risk management
- Information security officers
- Security incident investigation

### 4. Cost & Usage Dashboard

**Purpose**: Financial optimization and resource management

**Key Widgets:**

- Daily/Monthly Spend Trends
- Cost per Token Analysis
- Usage by Department/Team
- Budget vs. Actual Tracking
- Optimization Recommendations

**Target Audience:**

- FinOps teams
- Finance managers
- Cost optimization specialists
- Budget planners
- Resource allocation teams

## 📈 Custom Metrics

### Management Perspective KPIs

| Metric | Description | Target |
|--------|-------------|--------|
| **Daily Active Models** | Number of unique models used | Trending up |
| **Average Response Time** | Mean response time across all calls | < 2 seconds |
| **Success Rate** | Percentage of successful API calls | > 99.5% |
| **Cost per Request** | Average cost per API invocation | Decreasing |
| **User Adoption** | Number of active users/applications | Growing |
| **Token Efficiency** | Useful output tokens vs. total tokens | > 80% |

### Technical Operations Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|----------------|
| **Error Rate** | Failed requests per minute | > 1% |
| **Throttling Rate** | Rate-limited requests | > 0.1% |
| **Latency P99** | 99th percentile response time | > 5 seconds |
| **Token Consumption** | Tokens processed per hour | Anomaly detection |
| **Concurrent Users** | Simultaneous active sessions | > 1000 |
| **Data Transfer** | Bytes transferred per hour | Anomaly detection |

## 🚨 Alerting

### Critical Alerts (Immediate Response)

- **Service Availability**: Bedrock API unavailable
- **High Error Rate**: >5% errors in 5-minute window
- **Security Incident**: Unauthorized access attempts
- **Cost Spike**: >200% increase in hourly spend
- **System Failure**: Infrastructure component down

### Warning Alerts (Next Business Day)

- **Performance Degradation**: Response times >3 seconds
- **Budget Threshold**: 80% of monthly budget reached
- **Unusual Patterns**: Anomalous usage detected
- **Compliance Issues**: Policy violations identified
- **Resource Limits**: Approaching service quotas

### Informational Alerts (Weekly Summary)

- **Usage Trends**: Weekly usage summary
- **Cost Optimization**: Potential savings identified
- **Performance Report**: System performance summary
- **Security Summary**: Security posture update
- **Compliance Status**: Regulatory compliance report

## 📋 Reporting

### Automated Reports

| Report Type | Frequency | Recipients | Content |
|-------------|-----------|------------|---------|
| **Daily Operations** | Daily | DevOps, SRE | System health, errors, performance |
| **Weekly Business** | Weekly | Management | Usage trends, costs, KPIs |
| **Monthly Executive** | Monthly | Leadership | ROI, strategic insights, forecasts |
| **Quarterly Compliance** | Quarterly | Compliance | Audit trails, policy adherence |
| **Annual Review** | Yearly | All stakeholders | Comprehensive analysis, planning |

### Custom Reporting

- **On-demand Analytics**: Generate reports for specific time periods
- **Incident Reports**: Detailed analysis of service disruptions
- **Capacity Planning**: Resource utilization and scaling recommendations
- **Security Assessments**: Threat analysis and mitigation strategies
- **Cost Analysis**: Detailed spending breakdown and optimization opportunities

## 🔒 Security Considerations

### Data Protection

- **Encryption at Rest**: All logs and data encrypted using AWS KMS
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Access Control**: Role-based access with least privilege principle
- **Data Classification**: Sensitive data identification and protection
- **Retention Policies**: Automated data lifecycle management

### Network Security

- **VPC Endpoints**: Private connectivity to AWS services
- **Security Groups**: Restrictive firewall rules
- **NACLs**: Network-level access control
- **WAF Integration**: Web application firewall protection
- **DDoS Protection**: AWS Shield integration

### Compliance Framework

- **SOC 2**: Security, availability, processing integrity, confidentiality, privacy
- **PCI DSS**: Payment card industry data security standards
- **HIPAA**: Healthcare information privacy and security
- **GDPR**: General data protection regulation compliance
- **FedRAMP**: Federal risk and authorization management program

## 💰 Cost Optimization

### Monitoring & Analysis

- **Real-time Cost Tracking**: Monitor spending as it occurs
- **Budget Alerts**: Proactive notifications before overspending
- **Usage Analytics**: Identify optimization opportunities
- **Resource Tagging**: Detailed cost allocation and chargeback
- **Trend Analysis**: Historical spending patterns and forecasting

### Optimization Strategies

| Strategy | Description | Potential Savings |
|----------|-------------|------------------|
| **Right-sizing Models** | Use appropriate model for each use case | 20-40% |
| **Prompt Optimization** | Reduce token usage through better prompts | 15-30% |
| **Batch Processing** | Group requests for efficiency | 10-25% |
| **Caching Results** | Avoid redundant API calls | 25-50% |
| **Usage Scheduling** | Time-based resource allocation | 10-20% |
| **Reserved Capacity** | Commit to usage for discounts | 10-30% |

### Cost Controls

- **Budget Enforcement**: Automatic spending limits
- **Resource Quotas**: Prevent runaway usage
- **Approval Workflows**: Governance for high-cost operations
- **Cost Allocation**: Department/project-based billing
- **Regular Reviews**: Monthly cost optimization sessions

## 🛠️ Troubleshooting

### Common Issues

#### 1. CloudFormation Deployment Failures

**Symptom**: Stack creation fails with permission errors

**Solution**:
```bash
# Verify IAM permissions
aws iam get-user
aws sts get-caller-identity

# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name bedrock-monitoring-infrastructure
```

#### 2. Lambda Function Timeouts

**Symptom**: Lambda functions timing out during execution

**Solution**:
```bash
# Increase timeout in CloudFormation template
Timeout: 300  # 5 minutes

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bedrock"
```

#### 3. Missing Bedrock Logs

**Symptom**: No logs appearing in CloudWatch

**Solution**:
```bash
# Verify logging configuration
python python-scripts/enable_bedrock_logging.py --verify

# Check IAM roles and permissions
aws iam get-role --role-name BedrockLoggingRole
```

#### 4. Dashboard Not Loading

**Symptom**: CloudWatch dashboards show no data

**Solution**:
```bash
# Verify metrics are being generated
aws cloudwatch list-metrics --namespace AWS/Bedrock

# Check dashboard configuration
aws cloudwatch get-dashboard --dashboard-name "Bedrock-Technical-Operations"
```

### Support Resources

- **Documentation**: Comprehensive guides in `/docs` folder
- **Log Analysis**: CloudWatch Insights queries for troubleshooting
- **Community Support**: GitHub issues and discussions
- **Professional Services**: AWS consulting and support options

## 🤝 Contributing

We welcome contributions to improve this monitoring solution!

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd bedrock-monitoring-system

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r python-scripts/requirements.txt

# Install development tools
pip install pytest black flake8
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comprehensive documentation
- Include unit tests for new features
- Ensure CloudFormation templates validate

### Testing

```bash
# Run Python tests
pytest python-scripts/tests/

# Validate CloudFormation templates
aws cloudformation validate-template --template-body file://cloudformation/bedrock-monitoring-infrastructure.yaml

# Check code formatting
black python-scripts/
flake8 python-scripts/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for AWS Bedrock monitoring and observability**