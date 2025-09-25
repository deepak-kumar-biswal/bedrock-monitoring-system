#!/bin/bash

# AWS Bedrock Monitoring Solution Deployment Script
# This script deploys the complete monitoring infrastructure

set -e

# Configuration
STACK_NAME_INFRA="bedrock-monitoring-infrastructure"
STACK_NAME_DASHBOARDS="bedrock-monitoring-dashboards"
REGION="us-east-1"
PARAMETERS_FILE="parameters.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        print_error "AWS CLI is not configured or not authenticated."
        print_error "Please run 'aws configure' to set up your credentials."
        exit 1
    fi
    print_status "AWS CLI is properly configured."
}

# Function to validate parameters file
validate_parameters() {
    print_status "Validating parameters file..."
    if [ ! -f "$PARAMETERS_FILE" ]; then
        print_error "Parameters file '$PARAMETERS_FILE' not found."
        exit 1
    fi
    
    # Check if email parameter is set
    EMAIL=$(cat $PARAMETERS_FILE | jq -r '.[] | select(.ParameterKey=="AlertEmail") | .ParameterValue')
    if [ "$EMAIL" == "admin@company.com" ]; then
        print_warning "Please update the AlertEmail parameter in $PARAMETERS_FILE with your actual email address."
        read -p "Enter your email address for alerts: " USER_EMAIL
        if [ ! -z "$USER_EMAIL" ]; then
            jq --arg email "$USER_EMAIL" '(.[] | select(.ParameterKey=="AlertEmail") | .ParameterValue) = $email' $PARAMETERS_FILE > tmp.$$.json && mv tmp.$$.json $PARAMETERS_FILE
            print_status "Email address updated to $USER_EMAIL"
        fi
    fi
}

# Function to deploy infrastructure stack
deploy_infrastructure() {
    print_status "Deploying infrastructure stack: $STACK_NAME_INFRA"
    
    aws cloudformation deploy \
        --template-file bedrock-monitoring-infrastructure.yaml \
        --stack-name $STACK_NAME_INFRA \
        --parameter-overrides file://$PARAMETERS_FILE \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region $REGION \
        --tags \
            Project=BedrockMonitoring \
            Environment=Production \
            Owner=DevOps
    
    if [ $? -eq 0 ]; then
        print_status "Infrastructure stack deployed successfully!"
    else
        print_error "Failed to deploy infrastructure stack."
        exit 1
    fi
}

# Function to deploy dashboards stack
deploy_dashboards() {
    print_status "Deploying dashboards stack: $STACK_NAME_DASHBOARDS"
    
    aws cloudformation deploy \
        --template-file bedrock-monitoring-dashboards.yaml \
        --stack-name $STACK_NAME_DASHBOARDS \
        --parameter-overrides \
            Environment=$(cat $PARAMETERS_FILE | jq -r '.[] | select(.ParameterKey=="Environment") | .ParameterValue') \
            InfrastructureStackName=$STACK_NAME_INFRA \
        --region $REGION \
        --tags \
            Project=BedrockMonitoring \
            Environment=Production \
            Owner=DevOps
    
    if [ $? -eq 0 ]; then
        print_status "Dashboards stack deployed successfully!"
    else
        print_error "Failed to deploy dashboards stack."
        exit 1
    fi
}

# Function to get stack outputs
get_outputs() {
    print_status "Retrieving stack outputs..."
    
    echo "Infrastructure Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME_INFRA \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo "Dashboard Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME_DASHBOARDS \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Function to enable Bedrock logging
enable_bedrock_logging() {
    print_status "Enabling AWS Bedrock model invocation logging..."
    
    # Get the environment from parameters
    ENV=$(cat $PARAMETERS_FILE | jq -r '.[] | select(.ParameterKey=="Environment") | .ParameterValue')
    
    # Check if Python script exists
    if [ -f "../python-scripts/enable_bedrock_logging.py" ]; then
        cd ../python-scripts
        python enable_bedrock_logging.py --region $REGION --environment $ENV
        cd ../cloudformation
        
        if [ $? -eq 0 ]; then
            print_status "Bedrock logging enabled successfully!"
        else
            print_warning "Failed to enable Bedrock logging automatically."
            print_warning "You can enable it manually by running:"
            print_warning "  cd python-scripts && python enable_bedrock_logging.py --region $REGION --environment $ENV"
        fi
    else
        print_warning "Bedrock logging script not found. Please run manually:"
        print_warning "  cd python-scripts && python enable_bedrock_logging.py --region $REGION --environment $ENV"
    fi
}

# Function to setup CloudWatch Log Insights queries
setup_log_insights() {
    print_status "Setting up CloudWatch Log Insights saved queries..."
    
    # Create saved queries for common investigations
    cat > queries.json << EOF
[
    {
        "name": "Top Users by API Calls",
        "queryString": "fields @timestamp, userIdentity.userName, eventName\\n| filter eventName like /Bedrock/\\n| stats count() as apiCalls by userIdentity.userName\\n| sort apiCalls desc\\n| limit 10",
        "logGroups": ["/aws/bedrock/application-logs/prod"]
    },
    {
        "name": "Error Analysis",
        "queryString": "fields @timestamp, errorCode, errorMessage, userIdentity.userName\\n| filter errorCode exists\\n| stats count() as errorCount by errorCode\\n| sort errorCount desc",
        "logGroups": ["/aws/bedrock/application-logs/prod"]
    },
    {
        "name": "Model Usage Patterns",
        "queryString": "fields @timestamp, requestParameters.modelId, responseElements.inputTokens, responseElements.outputTokens\\n| stats sum(responseElements.inputTokens) as totalInput, sum(responseElements.outputTokens) as totalOutput, count() as requests by requestParameters.modelId\\n| sort requests desc",
        "logGroups": ["/aws/bedrock/application-logs/prod"]
    }
]
EOF

    print_status "Saved queries configuration created in queries.json"
}

# Main deployment function
main() {
    print_status "Starting AWS Bedrock Monitoring Solution deployment..."
    
    check_aws_cli
    validate_parameters
    deploy_infrastructure
    deploy_dashboards
    enable_bedrock_logging
    get_outputs
    setup_log_insights
    
    print_status "✅ Deployment completed successfully!"
    print_status "Next steps:"
    echo "1. Configure your applications to send logs to the CloudWatch log groups"
    echo "2. Set up CloudWatch agents on your EC2 instances (if applicable)"
    echo "3. Access your dashboards using the URLs in the outputs above"
    echo "4. Configure additional alerts as needed"
    echo "5. Review and customize the saved CloudWatch Insights queries"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "delete")
        print_warning "This will delete all monitoring resources. Are you sure? (yes/no)"
        read -r confirmation
        if [ "$confirmation" = "yes" ]; then
            print_status "Deleting stacks..."
            aws cloudformation delete-stack --stack-name $STACK_NAME_DASHBOARDS --region $REGION
            aws cloudformation delete-stack --stack-name $STACK_NAME_INFRA --region $REGION
            print_status "Deletion initiated. Check AWS Console for progress."
        else
            print_status "Deletion cancelled."
        fi
        ;;
    "update")
        print_status "Updating existing stacks..."
        deploy_infrastructure
        deploy_dashboards
        ;;
    "status")
        print_status "Checking stack status..."
        aws cloudformation describe-stacks --stack-name $STACK_NAME_INFRA --region $REGION --query 'Stacks[0].StackStatus'
        aws cloudformation describe-stacks --stack-name $STACK_NAME_DASHBOARDS --region $REGION --query 'Stacks[0].StackStatus'
        ;;
    *)
        echo "Usage: $0 {deploy|delete|update|status}"
        echo "  deploy - Deploy the complete monitoring solution"
        echo "  delete - Delete all monitoring resources"
        echo "  update - Update existing stacks"
        echo "  status - Check the status of deployed stacks"
        exit 1
        ;;
esac