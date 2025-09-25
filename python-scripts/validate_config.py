"""
Configuration Validator for AWS Bedrock Monitoring Solution
Validates all configurations and prerequisites before deployment
"""

import boto3
import json
import os
import sys
from typing import Dict, List, Tuple
import re
from botocore.exceptions import ClientError, NoCredentialsError

class ConfigValidator:
    """
    Validates configuration for Bedrock monitoring deployment
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_messages = []
        
    def validate_all(self) -> bool:
        """
        Run all validation checks
        
        Returns:
            True if all validations pass, False otherwise
        """
        print("🔍 Starting configuration validation...")
        print("=" * 50)
        
        # Run all validation checks
        self.validate_aws_credentials()
        self.validate_aws_permissions()
        self.validate_parameters_file()
        self.validate_email_configuration()
        self.validate_python_environment()
        self.validate_cloudformation_templates()
        
        self.print_results()
        
        return len(self.errors) == 0
    
    def validate_aws_credentials(self):
        """Validate AWS credentials are configured"""
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            
            self.success_messages.append(
                f"✅ AWS credentials configured for account: {identity['Account']}"
            )
            self.success_messages.append(
                f"✅ Using IAM principal: {identity['Arn']}"
            )
            
        except NoCredentialsError:
            self.errors.append("❌ AWS credentials not configured. Run 'aws configure'")
        except Exception as e:
            self.errors.append(f"❌ Error validating AWS credentials: {str(e)}")
    
    def validate_aws_permissions(self):
        """Validate required AWS permissions"""
        required_permissions = [
            ('cloudformation', 'list_stacks'),
            ('cloudwatch', 'list_dashboards'),
            ('logs', 'describe_log_groups'),
            ('s3', 'list_buckets'),
            ('lambda', 'list_functions'),
            ('sns', 'list_topics'),
            ('iam', 'list_roles')
        ]
        
        for service_name, operation in required_permissions:
            try:
                client = boto3.client(service_name)
                method = getattr(client, operation)
                method()
                self.success_messages.append(f"✅ {service_name.upper()} permissions validated")
            except ClientError as e:
                if e.response['Error']['Code'] in ['AccessDenied', 'UnauthorizedOperation']:
                    self.errors.append(f"❌ Missing {service_name.upper()} permissions")
                else:
                    self.warnings.append(f"⚠️  Could not validate {service_name.upper()} permissions: {e}")
            except Exception as e:
                self.warnings.append(f"⚠️  Error checking {service_name.upper()} permissions: {e}")
    
    def validate_parameters_file(self):
        """Validate CloudFormation parameters file"""
        params_file = 'cloudformation/parameters.json'
        
        if not os.path.exists(params_file):
            self.errors.append(f"❌ Parameters file not found: {params_file}")
            return
        
        try:
            with open(params_file, 'r') as f:
                params = json.load(f)
            
            # Validate structure
            if not isinstance(params, list):
                self.errors.append("❌ Parameters file must contain an array of parameters")
                return
            
            # Required parameters
            required_params = ['Environment', 'AlertEmail', 'CloudTrailRetentionDays', 'CloudWatchLogRetentionDays']
            param_keys = [p.get('ParameterKey') for p in params]
            
            for required in required_params:
                if required not in param_keys:
                    self.errors.append(f"❌ Missing required parameter: {required}")
                else:
                    self.success_messages.append(f"✅ Found required parameter: {required}")
            
            # Validate parameter values
            for param in params:
                key = param.get('ParameterKey')
                value = param.get('ParameterValue')
                
                if key == 'AlertEmail' and value:
                    if not self.is_valid_email(value):
                        self.errors.append(f"❌ Invalid email format: {value}")
                    elif value == 'admin@company.com':
                        self.warnings.append("⚠️  Using default email address. Update with your actual email.")
                    else:
                        self.success_messages.append(f"✅ Valid email configured: {value}")
                
                if key == 'Environment' and value not in ['dev', 'staging', 'prod']:
                    self.warnings.append(f"⚠️  Unusual environment value: {value}")
                
                if key in ['CloudTrailRetentionDays', 'CloudWatchLogRetentionDays']:
                    try:
                        days = int(value)
                        if days < 1 or days > 3653:  # 10 years max
                            self.warnings.append(f"⚠️  Unusual retention period for {key}: {days} days")
                    except ValueError:
                        self.errors.append(f"❌ Invalid retention days value for {key}: {value}")
                        
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ Invalid JSON in parameters file: {e}")
        except Exception as e:
            self.errors.append(f"❌ Error reading parameters file: {e}")
    
    def validate_email_configuration(self):
        """Validate SES email configuration"""
        try:
            ses = boto3.client('ses')
            verified_emails = ses.list_verified_email_addresses()
            
            # Read email from parameters
            params_file = 'cloudformation/parameters.json'
            if os.path.exists(params_file):
                with open(params_file, 'r') as f:
                    params = json.load(f)
                
                alert_email = None
                for param in params:
                    if param.get('ParameterKey') == 'AlertEmail':
                        alert_email = param.get('ParameterValue')
                        break
                
                if alert_email and alert_email != 'admin@company.com':
                    if alert_email in verified_emails['VerifiedEmailAddresses']:
                        self.success_messages.append(f"✅ Email verified in SES: {alert_email}")
                    else:
                        self.warnings.append(f"⚠️  Email not verified in SES: {alert_email}")
                        self.warnings.append("   Run: aws ses verify-email-identity --email-address your-email@domain.com")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                self.warnings.append("⚠️  Cannot validate SES configuration - missing permissions")
            else:
                self.warnings.append(f"⚠️  SES validation error: {e}")
        except Exception as e:
            self.warnings.append(f"⚠️  Error checking SES configuration: {e}")
    
    def validate_python_environment(self):
        """Validate Python environment and dependencies"""
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 10):
            self.errors.append(f"❌ Python 3.10+ required, found {python_version.major}.{python_version.minor}")
        else:
            self.success_messages.append(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
        
        # Check required packages
        required_packages = [
            'boto3', 'pandas', 'matplotlib', 'seaborn', 'jinja2', 'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                self.success_messages.append(f"✅ Package installed: {package}")
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.warnings.append(f"⚠️  Missing Python packages: {', '.join(missing_packages)}")
            self.warnings.append("   Run: pip install -r python-scripts/requirements.txt")
    
    def validate_cloudformation_templates(self):
        """Validate CloudFormation templates"""
        templates = [
            'cloudformation/bedrock-monitoring-infrastructure.yaml',
            'cloudformation/bedrock-monitoring-dashboards.yaml'
        ]
        
        cf = boto3.client('cloudformation')
        
        for template_path in templates:
            if not os.path.exists(template_path):
                self.errors.append(f"❌ CloudFormation template not found: {template_path}")
                continue
            
            try:
                with open(template_path, 'r') as f:
                    template_body = f.read()
                
                # Validate template syntax
                cf.validate_template(TemplateBody=template_body)
                self.success_messages.append(f"✅ Template validated: {template_path}")
                
            except ClientError as e:
                self.errors.append(f"❌ Template validation failed for {template_path}: {e}")
            except Exception as e:
                self.errors.append(f"❌ Error reading template {template_path}: {e}")
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 50)
        print("📊 VALIDATION RESULTS")
        print("=" * 50)
        
        if self.errors:
            print("\n❌ ERRORS (Must be fixed before deployment):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS (Recommended to address):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.success_messages:
            print("\n✅ SUCCESS:")
            for success in self.success_messages:
                print(f"   {success}")
        
        print("\n" + "=" * 50)
        
        if self.errors:
            print(f"❌ VALIDATION FAILED: {len(self.errors)} error(s) found")
            print("🔧 Please fix the errors above before proceeding with deployment.")
        else:
            print("✅ VALIDATION PASSED: Ready for deployment!")
            if self.warnings:
                print(f"⚠️  {len(self.warnings)} warning(s) found - review recommendations above.")
        
        print("=" * 50)
    
    def generate_fix_suggestions(self) -> List[str]:
        """Generate specific fix suggestions based on errors found"""
        suggestions = []
        
        for error in self.errors:
            if "AWS credentials not configured" in error:
                suggestions.append("Run 'aws configure' to set up your AWS credentials")
            elif "Parameters file not found" in error:
                suggestions.append("Create cloudformation/parameters.json with required parameters")
            elif "Invalid email format" in error:
                suggestions.append("Update AlertEmail in parameters.json with a valid email address")
            elif "Python 3.9+" in error:
                suggestions.append("Install Python 3.9 or higher")
            elif "Missing Python packages" in error:
                suggestions.append("Run 'pip install -r python-scripts/requirements.txt'")
            elif "CloudFormation template not found" in error:
                suggestions.append("Ensure all CloudFormation templates are in the correct location")
        
        return suggestions

def main():
    """Main validation function"""
    validator = ConfigValidator()
    
    print("🚀 AWS Bedrock Monitoring Solution - Configuration Validator")
    print("This tool validates your environment before deployment.\n")
    
    # Run validation
    is_valid = validator.validate_all()
    
    # Generate fix suggestions if there are errors
    if not is_valid:
        suggestions = validator.generate_fix_suggestions()
        if suggestions:
            print("\n🔧 SUGGESTED FIXES:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()