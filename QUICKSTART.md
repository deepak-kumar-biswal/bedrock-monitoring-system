# Quick Deployment Guide

## Prerequisites Checklist
- [ ] AWS CLI installed and configured
- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Email address verified in SES (for reports)
- [ ] IAM permissions configured

## Step-by-Step Deployment

### 1. Repository Setup
```bash
git clone <your-repo-url>
cd bedrock-monitoring
```

### 2. Parameter Configuration
Edit `cloudformation/parameters.json`:
```json
{
  "Environment": "prod",
  "AlertEmail": "YOUR_EMAIL@company.com",
  "CloudTrailRetentionDays": "90",
  "CloudWatchLogRetentionDays": "30",
  "EnableDetailedMonitoring": "true"
}
```

### 3. Deploy Infrastructure
```bash
cd cloudformation
chmod +x deploy.sh
./deploy.sh deploy
```

### 4. Install Python Dependencies
```bash
cd ../python-scripts
pip install -r requirements.txt
```

### 5. Generate Architecture Diagrams
```bash
cd ../docs
python architecture_diagram.py
```

### 6. Test the Setup
```bash
# Test monitoring functions
cd ../python-scripts
python bedrock_monitor.py

# Test reporting
python bedrock_reporter.py
```

## Access Your Dashboards

After deployment, access your dashboards through:
1. AWS Console → CloudWatch → Dashboards
2. Look for dashboards named:
   - `Bedrock-Technical-Operations-{Environment}`
   - `Bedrock-Management-Overview-{Environment}`
   - `Bedrock-Security-Monitoring-{Environment}`
   - `Bedrock-Cost-Usage-{Environment}`

## Next Steps

1. **Configure Alerts**: Set up additional alert thresholds
2. **Customize Dashboards**: Modify widgets for your specific needs
3. **Set Up Reporting**: Configure automated report recipients
4. **Enable SES**: Verify email addresses for report delivery
5. **Review Security**: Implement additional security measures if needed

## Estimated Costs
- **Small deployment** (< 1000 API calls/day): ~$50/month
- **Medium deployment** (< 10,000 API calls/day): ~$150/month
- **Large deployment** (> 100,000 API calls/day): ~$500/month

## Support
- Check the main README.md for detailed documentation
- Review CloudFormation stack events for deployment issues
- Use AWS CloudWatch Logs for debugging Lambda functions