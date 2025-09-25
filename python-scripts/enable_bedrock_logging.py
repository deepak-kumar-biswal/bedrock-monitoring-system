"""
AWS Bedrock Logging Enablement Script
This script enables comprehensive logging for AWS Bedrock services
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BedrockLoggingEnabler:
    """
    Enables and configures logging for AWS Bedrock services
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the Bedrock logging enabler
        
        Args:
            region_name: AWS region to configure logging
        """
        self.region_name = region_name
        self.bedrock_client = boto3.client('bedrock', region_name=region_name)
        self.logs_client = boto3.client('logs', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        
    def enable_model_invocation_logging(
        self, 
        log_group_name: str,
        s3_bucket_name: str,
        s3_key_prefix: str = 'bedrock-logs/',
        role_arn: str = None
    ) -> bool:
        """
        Enable Bedrock model invocation logging
        
        Args:
            log_group_name: CloudWatch Log Group name
            s3_bucket_name: S3 bucket for logs
            s3_key_prefix: S3 key prefix for logs
            role_arn: IAM role ARN for logging (optional)
            
        Returns:
            True if logging enabled successfully, False otherwise
        """
        try:
            # Prepare logging configuration
            logging_config = {
                'cloudWatchConfig': {
                    'logGroupName': log_group_name
                },
                's3Config': {
                    'bucketName': s3_bucket_name,
                    'keyPrefix': s3_key_prefix
                },
                'textDataDeliveryEnabled': True,
                'imageDataDeliveryEnabled': True,
                'embeddingDataDeliveryEnabled': True
            }
            
            # Add role ARN if provided
            if role_arn:
                logging_config['cloudWatchConfig']['roleArn'] = role_arn
            
            # Enable model invocation logging
            response = self.bedrock_client.put_model_invocation_logging_configuration(
                loggingConfig=logging_config
            )
            
            logger.info("✅ Bedrock model invocation logging enabled successfully")
            logger.info(f"   Log Group: {log_group_name}")
            logger.info(f"   S3 Bucket: {s3_bucket_name}")
            logger.info(f"   S3 Prefix: {s3_key_prefix}")
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ValidationException':
                logger.error(f"❌ Validation error: {error_message}")
                logger.error("   Check if the log group and S3 bucket exist and are accessible")
            elif error_code == 'AccessDeniedException':
                logger.error(f"❌ Access denied: {error_message}")
                logger.error("   Check IAM permissions for bedrock:PutModelInvocationLoggingConfiguration")
            else:
                logger.error(f"❌ Error enabling Bedrock logging: {error_code} - {error_message}")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error enabling Bedrock logging: {str(e)}")
            return False
    
    def get_model_invocation_logging_configuration(self) -> Optional[Dict[str, Any]]:
        """
        Get current Bedrock model invocation logging configuration
        
        Returns:
            Current logging configuration or None if not configured
        """
        try:
            response = self.bedrock_client.get_model_invocation_logging_configuration()
            return response.get('loggingConfig')
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info("ℹ️  No model invocation logging configuration found")
                return None
            else:
                logger.error(f"❌ Error getting logging configuration: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Unexpected error getting logging configuration: {str(e)}")
            return None
    
    def disable_model_invocation_logging(self) -> bool:
        """
        Disable Bedrock model invocation logging
        
        Returns:
            True if logging disabled successfully, False otherwise
        """
        try:
            self.bedrock_client.delete_model_invocation_logging_configuration()
            logger.info("✅ Bedrock model invocation logging disabled successfully")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Error disabling Bedrock logging: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error disabling Bedrock logging: {str(e)}")
            return False
    
    def verify_logging_setup(self, log_group_name: str, s3_bucket_name: str) -> Dict[str, bool]:
        """
        Verify that logging prerequisites are in place
        
        Args:
            log_group_name: CloudWatch Log Group name to verify
            s3_bucket_name: S3 bucket name to verify
            
        Returns:
            Dictionary with verification results
        """
        results = {
            'log_group_exists': False,
            's3_bucket_exists': False,
            'bedrock_logging_enabled': False
        }
        
        # Check if CloudWatch Log Group exists
        try:
            self.logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
            results['log_group_exists'] = True
            logger.info(f"✅ CloudWatch Log Group exists: {log_group_name}")
        except ClientError:
            logger.warning(f"⚠️  CloudWatch Log Group not found: {log_group_name}")
        
        # Check if S3 bucket exists
        try:
            self.s3_client.head_bucket(Bucket=s3_bucket_name)
            results['s3_bucket_exists'] = True
            logger.info(f"✅ S3 Bucket exists: {s3_bucket_name}")
        except ClientError:
            logger.warning(f"⚠️  S3 Bucket not found or not accessible: {s3_bucket_name}")
        
        # Check if Bedrock logging is enabled
        config = self.get_model_invocation_logging_configuration()
        if config:
            results['bedrock_logging_enabled'] = True
            logger.info("✅ Bedrock model invocation logging is enabled")
            logger.info(f"   Current config: {json.dumps(config, indent=2, default=str)}")
        else:
            logger.warning("⚠️  Bedrock model invocation logging is not enabled")
        
        return results
    
    def setup_comprehensive_logging(
        self, 
        environment: str = 'prod',
        account_id: str = None
    ) -> bool:
        """
        Set up comprehensive Bedrock logging with standard naming conventions
        
        Args:
            environment: Environment name (dev, staging, prod)
            account_id: AWS Account ID (will be fetched if not provided)
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Get account ID if not provided
            if not account_id:
                sts = boto3.client('sts')
                account_id = sts.get_caller_identity()['Account']
            
            # Define resource names
            log_group_name = f'/aws/bedrock/model-invocations/{environment}'
            s3_bucket_name = f'bedrock-model-invocations-{environment}-{account_id}'
            s3_key_prefix = f'model-invocations/{environment}/'
            
            logger.info(f"🚀 Setting up comprehensive Bedrock logging for environment: {environment}")
            logger.info(f"   Account ID: {account_id}")
            logger.info(f"   Region: {self.region_name}")
            
            # Verify prerequisites
            verification = self.verify_logging_setup(log_group_name, s3_bucket_name)
            
            if not verification['log_group_exists']:
                logger.error(f"❌ CloudWatch Log Group not found: {log_group_name}")
                logger.error("   Please ensure the CloudFormation stack has been deployed")
                return False
            
            if not verification['s3_bucket_exists']:
                logger.error(f"❌ S3 Bucket not found: {s3_bucket_name}")
                logger.error("   Please ensure the CloudFormation stack has been deployed")
                return False
            
            # Enable logging if not already enabled
            if not verification['bedrock_logging_enabled']:
                success = self.enable_model_invocation_logging(
                    log_group_name=log_group_name,
                    s3_bucket_name=s3_bucket_name,
                    s3_key_prefix=s3_key_prefix
                )
                
                if not success:
                    return False
            else:
                logger.info("ℹ️  Bedrock logging is already enabled")
            
            # Final verification
            final_verification = self.verify_logging_setup(log_group_name, s3_bucket_name)
            
            if all(final_verification.values()):
                logger.info("🎉 Comprehensive Bedrock logging setup completed successfully!")
                return True
            else:
                logger.error("❌ Logging setup verification failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error setting up comprehensive logging: {str(e)}")
            return False

def main():
    """
    Main function for enabling Bedrock logging
    """
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Enable AWS Bedrock Logging')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--environment', default='prod', help='Environment name')
    parser.add_argument('--verify-only', action='store_true', help='Only verify current configuration')
    parser.add_argument('--disable', action='store_true', help='Disable Bedrock logging')
    
    args = parser.parse_args()
    
    # Initialize the enabler
    enabler = BedrockLoggingEnabler(region_name=args.region)
    
    print("🔧 AWS Bedrock Logging Configuration Tool")
    print("=" * 50)
    
    if args.disable:
        print("⚠️  Disabling Bedrock model invocation logging...")
        success = enabler.disable_model_invocation_logging()
        if success:
            print("✅ Bedrock logging disabled successfully")
        else:
            print("❌ Failed to disable Bedrock logging")
        return
    
    if args.verify_only:
        print("🔍 Verifying current Bedrock logging configuration...")
        # Use environment-specific resource names
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        log_group_name = f'/aws/bedrock/model-invocations/{args.environment}'
        s3_bucket_name = f'bedrock-model-invocations-{args.environment}-{account_id}'
        
        verification = enabler.verify_logging_setup(log_group_name, s3_bucket_name)
        
        print("\n📊 Verification Results:")
        for check, result in verification.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {check.replace('_', ' ').title()}: {status}")
        
        return
    
    # Set up comprehensive logging
    success = enabler.setup_comprehensive_logging(environment=args.environment)
    
    if success:
        print("\n🎉 Bedrock logging has been successfully configured!")
        print("\nNext steps:")
        print("1. Your Bedrock model invocations will now be logged")
        print("2. Check CloudWatch Logs for real-time monitoring")
        print("3. Review S3 bucket for long-term log storage")
        print("4. Use the monitoring dashboards to analyze usage")
    else:
        print("\n❌ Failed to configure Bedrock logging")
        print("Please check the error messages above and resolve any issues")

if __name__ == "__main__":
    main()