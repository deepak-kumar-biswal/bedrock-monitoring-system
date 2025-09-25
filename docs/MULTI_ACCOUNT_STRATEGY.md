# Multi-Account AWS Bedrock Strategy & Enterprise Guardrails

## 🎯 **Your Question Answered**

**Q: How do we handle Bedrock monitoring when we have multiple AWS accounts? What are the best practices for enterprise-level guardrails?**

## 🏢 **Multi-Account Strategy**

### **Hub-and-Spoke Architecture**

```
┌─────────────────────────────────────────────┐
│            Management Account               │
│  • AWS Organizations + SCPs                 │
│  • Cross-account governance                 │
│  • Consolidated billing & budgets           │
└─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────┐
│         Security Hub Account                │
│  • Centralized log aggregation              │
│  • Enterprise dashboards                    │
│  • Cross-account analytics                  │
│  • Compliance reporting                     │
└─────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Dev Account │ │Prod Account │ │Test Account │
│• Local logs │ │• Enhanced   │ │• Sandbox    │
│• Basic      │ │  monitoring │ │  policies   │
│  policies   │ │• Strict     │ │• Learning   │
│• Fast dev   │ │  guardrails │ │  mode       │
└─────────────┘ └─────────────┘ └─────────────┘
```

### **Implementation Approach**

#### **1. CloudFormation StackSets Deployment**
- **Single template** deployed across all accounts
- **Environment-specific parameters** (dev/staging/prod)
- **Automated rollout** to new accounts
- **Consistent configuration** across organization

#### **2. Cross-Account Log Aggregation**
```yaml
# Each account streams logs to Security Hub
CrossAccountLogDestination:
  Type: AWS::Logs::Destination
  Properties:
    DestinationName: 'bedrock-logs-to-security-hub'
    TargetArn: 'arn:aws:logs:region:SECURITY-HUB:log-group:/enterprise/bedrock/aggregated-logs'
```

#### **3. Centralized Monitoring**
- **Security Hub Account**: Aggregates all Bedrock logs and metrics
- **Cross-account dashboards**: Unified view across all accounts
- **Centralized alerting**: Single point for enterprise notifications
- **Compliance reporting**: Organization-wide audit trails

## 🛡️ **Enterprise Guardrails Strategy**

### **4-Layer Defense Model**

#### **Layer 1: Service Control Policies (Organization Level)**
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
    },
    {
      "Sid": "RestrictToApprovedModels",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*",
      "Condition": {
        "ForAllValues:StringNotLike": {
          "bedrock:ModelId": [
            "anthropic.claude-3-sonnet-*",
            "amazon.titan-text-*"
          ]
        }
      }
    }
  ]
}
```

#### **Layer 2: Account-Level Controls**
- **AWS Config Rules**: Monitor compliance continuously
- **CloudWatch Alarms**: Alert on policy violations
- **IAM Policies**: Role-based access control
- **Budget Controls**: Prevent cost overruns

#### **Layer 3: Application-Level Policies**
- **Resource tagging**: Enforce cost allocation
- **Network isolation**: VPC endpoints only
- **Encryption**: KMS keys per environment
- **Access logging**: Detailed audit trails

#### **Layer 4: Runtime Content Filtering**
```yaml
BedrockGuardrail:
  Type: AWS::Bedrock::Guardrail
  Properties:
    Name: 'enterprise-content-filter'
    ContentPolicyConfig:
      FiltersConfig:
        - Type: HATE
          InputStrength: HIGH
          OutputStrength: HIGH
        - Type: VIOLENCE
          InputStrength: HIGH
          OutputStrength: HIGH
    SensitiveInformationPolicyConfig:
      PiiEntitiesConfig:
        - Type: EMAIL
          Action: BLOCK
        - Type: SSN
          Action: BLOCK
        - Type: CREDIT_DEBIT_CARD_NUMBER
          Action: BLOCK
```

## 🚀 **Best Practices Implementation**

### **Deployment Strategy**

#### **Phase 1: Foundation (Management Account)**
```bash
# Deploy Service Control Policies
aws organizations create-policy \
  --name "BedrockEnterpriseControls" \
  --type SERVICE_CONTROL_POLICY \
  --content file://scp-bedrock-enterprise-controls.json

# Apply to all OUs
aws organizations attach-policy \
  --policy-id p-xxxxxxxxxx \
  --target-id ou-xxxxxxxxxx
```

#### **Phase 2: Central Hub (Security Account)**
```bash
# Deploy centralized monitoring
aws cloudformation deploy \
  --template-file security-hub-account-template.yaml \
  --stack-name enterprise-bedrock-hub \
  --capabilities CAPABILITY_IAM
```

#### **Phase 3: Member Accounts (StackSets)**
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name "enterprise-bedrock-monitoring" \
  --template-body file://multi-account-stackset-template.yaml

# Deploy to all accounts
aws cloudformation create-stack-instances \
  --stack-set-name "enterprise-bedrock-monitoring" \
  --accounts "111111111111" "222222222222" "333333333333" \
  --regions "us-east-1" "us-west-2"
```

### **Governance Best Practices**

#### **1. Access Control**
- ✅ **Role-based access**: Different permissions per environment
- ✅ **MFA enforcement**: Required for all Bedrock access  
- ✅ **Time-limited access**: Temporary credentials for development
- ✅ **Regular audits**: Quarterly access reviews

#### **2. Cost Management**
- ✅ **Budget alerts**: Per-account spending limits
- ✅ **Token monitoring**: Track usage by team/project
- ✅ **Cost allocation**: Tags for chargeback
- ✅ **Optimization**: Automated recommendations

#### **3. Security Controls**
- ✅ **Encryption everywhere**: KMS for logs and data
- ✅ **Network isolation**: Private endpoints only
- ✅ **Content filtering**: Block sensitive information
- ✅ **Incident response**: Automated security workflows

#### **4. Compliance Framework**
- ✅ **Audit trails**: Complete API call logging
- ✅ **Data retention**: 7-year compliance storage
- ✅ **Regular assessments**: Automated compliance checks
- ✅ **Documentation**: Policy and procedure maintenance

## 📊 **Operational Benefits**

### **Centralized Visibility**
- **Single dashboard** for all accounts
- **Cross-account analytics** for usage patterns
- **Unified alerting** for security incidents
- **Consolidated reporting** for compliance

### **Consistent Governance**
- **Same policies** across all environments
- **Automated enforcement** via SCPs
- **Standardized guardrails** per account type
- **Predictable behavior** for developers

### **Cost Optimization**
- **Organization-wide** usage visibility
- **Bulk discount** negotiations
- **Waste identification** across accounts
- **Chargeback accuracy** by business unit

## 🎯 **Recommended File Structure**

```
bedrock-monitoring-system/
├── cloudformation/
│   ├── multi-account-stackset-template.yaml      # ← For member accounts
│   ├── security-hub-account-template.yaml        # ← For central hub
│   └── bedrock-monitoring-infrastructure.yaml    # ← Single account (existing)
├── governance/
│   ├── scp-bedrock-enterprise-controls.json      # ← Organization SCPs
│   ├── compliance-rules.yaml                     # ← AWS Config rules
│   └── budget-templates.yaml                     # ← Cost controls
├── docs/
│   ├── ENTERPRISE_DEPLOYMENT_GUIDE.md           # ← Step-by-step setup
│   ├── ENTERPRISE_MULTI_ACCOUNT_ARCHITECTURE.md # ← Architecture overview
│   └── GUARDRAILS_IMPLEMENTATION.md             # ← Security controls
└── scripts/
    ├── deploy-stackset.sh                        # ← Automated deployment
    └── setup-cross-account-logs.sh              # ← Log aggregation
```

## 💡 **Key Takeaways**

1. **Use StackSets** for consistent deployment across accounts
2. **Implement 4-layer security** (Organization → Account → Application → Runtime)
3. **Centralize logging and monitoring** in dedicated Security Hub account
4. **Enforce policies via SCPs** at the organization level
5. **Automate compliance checking** with AWS Config rules
6. **Monitor costs proactively** with budgets and alerts
7. **Plan for scale** with automated onboarding procedures

This enterprise approach provides **comprehensive governance, security, and cost control** while maintaining **operational efficiency** across all AWS accounts using Bedrock services.