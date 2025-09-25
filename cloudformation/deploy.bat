@echo off
REM AWS Bedrock Monitoring Solution Deployment Script for Windows
REM This script deploys the complete monitoring infrastructure

setlocal enabledelayedexpansion

REM Configuration
set STACK_NAME_INFRA=bedrock-monitoring-infrastructure
set STACK_NAME_DASHBOARDS=bedrock-monitoring-dashboards
set REGION=us-east-1
set PARAMETERS_FILE=parameters.json

echo [INFO] Starting AWS Bedrock Monitoring Solution deployment...

REM Function to check if AWS CLI is configured
echo [INFO] Checking AWS CLI configuration...
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] AWS CLI is not configured or not authenticated.
    echo [ERROR] Please run 'aws configure' to set up your credentials.
    exit /b 1
)
echo [INFO] AWS CLI is properly configured.

REM Function to validate parameters file
echo [INFO] Validating parameters file...
if not exist "%PARAMETERS_FILE%" (
    echo [ERROR] Parameters file '%PARAMETERS_FILE%' not found.
    exit /b 1
)

REM Check if email parameter needs to be updated
findstr "admin@company.com" %PARAMETERS_FILE% >nul
if %errorlevel% equ 0 (
    echo [WARNING] Please update the AlertEmail parameter in %PARAMETERS_FILE% with your actual email address.
    set /p USER_EMAIL="Enter your email address for alerts: "
    if not "!USER_EMAIL!"=="" (
        powershell -Command "(Get-Content %PARAMETERS_FILE%) -replace 'admin@company.com', '!USER_EMAIL!' | Set-Content %PARAMETERS_FILE%"
        echo [INFO] Email address updated to !USER_EMAIL!
    )
)

REM Function to deploy infrastructure stack
echo [INFO] Deploying infrastructure stack: %STACK_NAME_INFRA%

aws cloudformation deploy ^
    --template-file bedrock-monitoring-infrastructure.yaml ^
    --stack-name %STACK_NAME_INFRA% ^
    --parameter-overrides file://%PARAMETERS_FILE% ^
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM ^
    --region %REGION% ^
    --tags ^
        Project=BedrockMonitoring ^
        Environment=Production ^
        Owner=DevOps

if %errorlevel% neq 0 (
    echo [ERROR] Failed to deploy infrastructure stack.
    exit /b 1
)
echo [INFO] Infrastructure stack deployed successfully!

REM Function to deploy dashboards stack
echo [INFO] Deploying dashboards stack: %STACK_NAME_DASHBOARDS%

REM Extract environment from parameters file
for /f "tokens=2 delims=:" %%a in ('findstr "Environment" %PARAMETERS_FILE%') do (
    set ENV_VALUE=%%a
    set ENV_VALUE=!ENV_VALUE: =!
    set ENV_VALUE=!ENV_VALUE:"=!
    set ENV_VALUE=!ENV_VALUE:,=!
)

aws cloudformation deploy ^
    --template-file bedrock-monitoring-dashboards.yaml ^
    --stack-name %STACK_NAME_DASHBOARDS% ^
    --parameter-overrides ^
        Environment=!ENV_VALUE! ^
        InfrastructureStackName=%STACK_NAME_INFRA% ^
    --region %REGION% ^
    --tags ^
        Project=BedrockMonitoring ^
        Environment=Production ^
        Owner=DevOps

if %errorlevel% neq 0 (
    echo [ERROR] Failed to deploy dashboards stack.
    exit /b 1
)
echo [INFO] Dashboards stack deployed successfully!

REM Function to enable Bedrock logging
echo [INFO] Enabling AWS Bedrock model invocation logging...

REM Check if Python script exists
if exist "..\python-scripts\enable_bedrock_logging.py" (
    cd ..\python-scripts
    python enable_bedrock_logging.py --region %REGION% --environment !ENV_VALUE!
    cd ..\cloudformation
    
    if !errorlevel! equ 0 (
        echo [INFO] ✅ Bedrock logging enabled successfully!
    ) else (
        echo [WARNING] ⚠️  Failed to enable Bedrock logging automatically.
        echo [WARNING] You can enable it manually by running:
        echo [WARNING]   cd python-scripts ^&^& python enable_bedrock_logging.py --region %REGION% --environment !ENV_VALUE!
    )
) else (
    echo [WARNING] ⚠️  Bedrock logging script not found. Please run manually:
    echo [WARNING]   cd python-scripts ^&^& python enable_bedrock_logging.py --region %REGION% --environment !ENV_VALUE!
)

REM Function to get stack outputs
echo [INFO] Retrieving stack outputs...

echo Infrastructure Stack Outputs:
aws cloudformation describe-stacks ^
    --stack-name %STACK_NAME_INFRA% ^
    --region %REGION% ^
    --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" ^
    --output table

echo Dashboard Stack Outputs:
aws cloudformation describe-stacks ^
    --stack-name %STACK_NAME_DASHBOARDS% ^
    --region %REGION% ^
    --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" ^
    --output table

REM Handle command line arguments
if "%1"=="delete" (
    echo [WARNING] This will delete all monitoring resources. Are you sure? (yes/no)
    set /p confirmation=
    if "!confirmation!"=="yes" (
        echo [INFO] Deleting stacks...
        aws cloudformation delete-stack --stack-name %STACK_NAME_DASHBOARDS% --region %REGION%
        aws cloudformation delete-stack --stack-name %STACK_NAME_INFRA% --region %REGION%
        echo [INFO] Deletion initiated. Check AWS Console for progress.
    ) else (
        echo [INFO] Deletion cancelled.
    )
    goto :end
)

if "%1"=="update" (
    echo [INFO] Updating existing stacks...
    goto :deploy_infra
)

if "%1"=="status" (
    echo [INFO] Checking stack status...
    aws cloudformation describe-stacks --stack-name %STACK_NAME_INFRA% --region %REGION% --query "Stacks[0].StackStatus"
    aws cloudformation describe-stacks --stack-name %STACK_NAME_DASHBOARDS% --region %REGION% --query "Stacks[0].StackStatus"
    goto :end
)

echo [INFO] ✅ Deployment completed successfully!
echo [INFO] Next steps:
echo 1. Configure your applications to send logs to the CloudWatch log groups
echo 2. Set up CloudWatch agents on your EC2 instances (if applicable)
echo 3. Access your dashboards using the URLs in the outputs above
echo 4. Configure additional alerts as needed
echo 5. Review and customize the saved CloudWatch Insights queries

:end
endlocal