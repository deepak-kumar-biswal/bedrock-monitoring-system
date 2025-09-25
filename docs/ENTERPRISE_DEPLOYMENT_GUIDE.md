# Enterprise Multi-Account Bedrock Deployment Guide

## 🎯 **Overview**

This guide provides step-by-step instructions for deploying enterprise-grade Bedrock monitoring across multiple AWS accounts with comprehensive governance and guardrails.

## 🏗️ **Architecture Summary**

```
Management Account (AWS Organizations)
├── Service Control Policies (SCPs)
├── StackSets Management
└── Cost & Billing Consolidation

Security Hub Account (Centralized Monitoring)
├── Aggregated Log Collection
├── Enterprise Dashboards
├── Cross-Account Analytics
└── Compliance Reporting

Member Accounts (Dev/Staging/Prod/Sandbox)
├── Local Bedrock Logging
├── Account-Specific Guardrails
├── Cross-Account Log Streaming
└── Environment-Specific Policies
```

## 📋 **Prerequisites**

### Management Account Setup
- [ ] AWS Organizations enabled
- [ ] AWS Control Tower deployed (recommended)
- [ ] AWS Config enabled organization-wide
- [ ] AWS CloudTrail organization trail configured

### Security Hub Account
- [ ] Dedicated security/logging account created
- [ ] Cross-account access roles configured
- [ ] Sufficient S3 and CloudWatch Logs quotas

### Member Accounts
- [ ] Accounts created via AWS Organizations
- [ ] OrganizationAccountAccessRole available
- [ ] Bedrock service enabled in required regions

## 🚀 **Step-by-Step Deployment**

### Phase 1: Service Control Policies (Management Account)

```bash
# 1. Apply Bedrock governance SCPs
aws organizations create-policy \
  --name "BedrockEnterpriseControls" \
  --description "Enterprise controls for Bedrock usage" \
  --type SERVICE_CONTROL_POLICY \
  --content file://governance/scp-bedrock-enterprise-controls.json

# 2. Attach SCP to organizational units
aws organizations attach-policy \
  --policy-id p-xxxxxxxxxx \
  --target-id ou-xxxxxxxxxx
```

### Phase 2: Security Hub Account Deployment

```bash
# Deploy central monitoring infrastructure
aws cloudformation deploy \
  --template-file cloudformation/security-hub-account-template.yaml \
  --stack-name enterprise-bedrock-security-hub \
  --parameter-overrides \
    OrganizationId=o-xxxxxxxxxx \
    MemberAccountIds="111111111111,222222222222,333333333333" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Phase 3: StackSet Deployment to Member Accounts

```bash
# Create StackSet for multi-account deployment
aws cloudformation create-stack-set \
  --stack-set-name "enterprise-bedrock-monitoring" \
  --template-body file://cloudformation/multi-account-stackset-template.yaml \
  --parameters \
    ParameterKey=SecurityHubAccountId,ParameterValue=555555555555 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --administration-role-arn arn:aws:iam::MANAGEMENT-ACCOUNT:role/AWSCloudFormationStackSetAdministrationRole \
  --execution-role-name AWSCloudFormationStackSetExecutionRole

# Deploy to target accounts and regions
aws cloudformation create-stack-instances \
  --stack-set-name "enterprise-bedrock-monitoring" \
  --accounts "111111111111" "222222222222" "333333333333" \
  --regions "us-east-1" "us-west-2" "eu-west-1" \
  --parameter-overrides \
    ParameterKey=Environment,ParameterValue=prod \
    ParameterKey=AlertEmail,ParameterValue=bedrock-alerts@company.com \
    ParameterKey=ComplianceRequirement,ParameterValue=SOC2
```

### Phase 4: Enable Cross-Account Log Aggregation

```bash
# Create cross-account trust relationships
aws logs put-destination \
  --destination-name "enterprise-bedrock-logs" \
  --target-arn "arn:aws:logs:us-east-1:SECURITY-HUB-ACCOUNT:log-group:/enterprise/bedrock/aggregated-logs" \
  --role-arn "arn:aws:iam::MEMBER-ACCOUNT:role/BedrockCrossAccountLogRole"

# Create subscription filters in each member account
aws logs put-subscription-filter \
  --log-group-name "/aws/bedrock/model-invocations-prod" \
  --filter-name "enterprise-bedrock-filter" \
  --filter-pattern "" \
  --destination-arn "arn:aws:logs:us-east-1:SECURITY-HUB-ACCOUNT:destination:enterprise-bedrock-logs"
```

## 🛡️ **Guardrails Implementation Strategy**

### Level 1: Organization-Wide Controls (SCPs)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceBedockLoggingRequirement",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "bedrock:ModelInvocationLoggingEnabled": "false"
        }
      }
    }
  ]
}
```

### Level 2: Account-Level Governance

- **AWS Config Rules**: Monitor compliance with logging requirements
- **CloudWatch Alarms**: Alert on unusual usage patterns
- **IAM Policies**: Restrict access to approved models only
- **Resource Tags**: Enforce cost allocation and governance tags

### Level 3: Application-Level Controls

- **Bedrock Guardrails**: Content filtering and safety controls
- **Token Limits**: Prevent excessive usage per request
- **Rate Limiting**: Control API call frequency
- **Model Restrictions**: Limit to approved foundation models

### Level 4: Runtime Content Filtering

```yaml
# Bedrock Guardrail Configuration
BedrockGuardrail:
  Type: AWS::Bedrock::Guardrail
  Properties:
    ContentPolicyConfig:
      FiltersConfig:
        - Type: HATE
          InputStrength: HIGH
          OutputStrength: HIGH
    SensitiveInformationPolicyConfig:
      PiiEntitiesConfig:
        - Type: EMAIL
          Action: BLOCK
        - Type: SSN
          Action: BLOCK
```

## 📊 **Monitoring & Analytics**

### Enterprise Dashboards

1. **Executive Dashboard**
   - Total Bedrock spend across all accounts
   - Usage trends by business unit
   - Compliance status overview
   - Security incident summary

2. **Technical Operations Dashboard**
   - Model performance by account
   - Error rates and troubleshooting
   - Token usage optimization opportunities
   - Infrastructure health metrics

3. **Security Dashboard**
   - Guardrail violations by account
   - Unusual access patterns
   - PII detection incidents
   - Compliance audit trails

### Key Metrics to Track

| Metric Category | Key Indicators | Monitoring Frequency |
|----------------|----------------|---------------------|
| **Usage** | Tokens/day by account, Model invocations/hour | Real-time |
| **Cost** | Daily spend by account, Cost per token | Daily |
| **Security** | Guardrail violations, PII detections | Real-time |
| **Compliance** | Policy violations, Audit trail completeness | Daily |
| **Performance** | Model response times, Error rates | Real-time |

## 🎛️ **Operational Procedures**

### New Account Onboarding

1. **Account Creation**
   ```bash
   # Create new account via Organizations
   aws organizations create-account \
     --email new-account@company.com \
     --account-name "New Business Unit - Prod"
   ```

2. **StackSet Deployment**
   ```bash
   # Add new account to existing StackSet
   aws cloudformation create-stack-instances \
     --stack-set-name "enterprise-bedrock-monitoring" \
     --accounts "NEW-ACCOUNT-ID" \
     --regions "us-east-1"
   ```

3. **Guardrail Configuration**
   - Apply appropriate SCPs based on account purpose
   - Configure environment-specific Bedrock guardrails
   - Set up account-specific alerting and dashboards

### Incident Response

1. **Guardrail Violation**
   - Automatic blocking via Bedrock guardrails
   - SNS notification to security team
   - CloudWatch alarm triggers investigation workflow

2. **Unusual Usage Pattern**
   - CloudWatch anomaly detection alerts
   - Automatic scaling restrictions if needed
   - Investigation via centralized logs

3. **Compliance Violation**
   - AWS Config rule triggers remediation
   - Automatic policy enforcement via Lambda
   - Audit trail documentation

## 💰 **Cost Management**

### Budget Controls

```yaml
# Budget for each account
BedrockBudget:
  Type: AWS::Budgets::Budget
  Properties:
    Budget:
      BudgetName: !Sub 'bedrock-budget-${Environment}'
      BudgetLimit:
        Amount: 10000  # $10,000/month
        Unit: USD
      TimeUnit: MONTHLY
      BudgetType: COST
      CostFilters:
        Service: ['Amazon Bedrock']
```

### Cost Optimization

- **Token Usage Analytics**: Identify opportunities to optimize prompts
- **Model Selection**: Guide users to most cost-effective models
- **Usage Patterns**: Detect and address inefficient usage
- **Reserved Capacity**: Plan for predictable workloads

## 🔒 **Security Best Practices**

### Access Control

1. **Principle of Least Privilege**
   - Role-based access to specific models only
   - Time-limited access for development/testing
   - Regular access reviews and cleanup

2. **Multi-Factor Authentication**
   - Enforce MFA for all Bedrock access
   - Use AWS SSO for centralized identity management
   - Regular rotation of access keys

3. **Network Security**
   - VPC endpoints for Bedrock API calls
   - Private subnet deployment where possible
   - Security group restrictions

### Data Protection

1. **Encryption**
   - KMS encryption for all logs and data
   - Separate keys per environment/account
   - Regular key rotation

2. **Data Classification**
   - Tag all Bedrock resources with data classification
   - Implement data retention policies
   - Monitor for sensitive data exposure

## 📋 **Compliance Framework**

### SOC 2 Compliance

- **Security**: Access controls, encryption, monitoring
- **Availability**: High availability, disaster recovery
- **Processing Integrity**: Data validation, error handling
- **Confidentiality**: Data classification, access restrictions
- **Privacy**: PII protection, data retention

### Implementation Checklist

- [ ] Logging enabled for all Bedrock activities
- [ ] Access controls documented and tested
- [ ] Incident response procedures defined
- [ ] Regular security assessments scheduled
- [ ] Compliance reporting automated

## 🚨 **Alerting Strategy**

### Critical Alerts (Immediate Response)

- Guardrail violations
- Unusual spending patterns (>50% increase)
- Security policy violations
- Service availability issues

### Warning Alerts (Next Business Day)

- Budget threshold exceeded (80%)
- Performance degradation
- Compliance rule violations
- Resource quota limits approached

### Informational Alerts (Weekly Summary)

- Usage trend reports
- Cost optimization opportunities
- Security posture summary
- Compliance status update

This comprehensive approach ensures enterprise-grade governance, security, and monitoring for Bedrock across all AWS accounts while maintaining operational efficiency and cost control.