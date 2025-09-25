"""
AWS Bedrock Custom Metrics Collection and Analysis
This module provides comprehensive monitoring capabilities for AWS Bedrock services
"""

import boto3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BedrockMonitor:
    """
    Main class for monitoring AWS Bedrock services
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the Bedrock monitor
        
        Args:
            region_name: AWS region to monitor
        """
        self.region_name = region_name
        self.bedrock_client = boto3.client('bedrock', region_name=region_name)
        self.bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
        self.logs_client = boto3.client('logs', region_name=region_name)
        self.sns_client = boto3.client('sns', region_name=region_name)
        
        # Environment variables
        self.environment = os.getenv('ENVIRONMENT', 'prod')
        self.sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
        
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available Bedrock models
        
        Returns:
            List of available models with their details
        """
        try:
            response = self.bedrock_client.list_foundation_models()
            return response.get('modelSummaries', [])
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            return []
    
    def collect_usage_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Collect usage metrics from CloudWatch
        
        Args:
            start_time: Start time for metrics collection
            end_time: End time for metrics collection
            
        Returns:
            Dictionary containing usage metrics
        """
        metrics = {
            'total_invocations': 0,
            'total_errors': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'avg_duration': 0,
            'model_usage': defaultdict(int),
            'error_distribution': defaultdict(int),
            'hourly_usage': defaultdict(int)
        }
        
        try:
            # Get invocation metrics
            invocations = self._get_cloudwatch_metric(
                'AWS/Bedrock', 'Invocations', start_time, end_time, 'Sum'
            )
            metrics['total_invocations'] = sum(point['Sum'] for point in invocations)
            
            # Get error metrics
            errors = self._get_cloudwatch_metric(
                'AWS/Bedrock', 'Errors', start_time, end_time, 'Sum'
            )
            metrics['total_errors'] = sum(point['Sum'] for point in errors)
            
            # Get token metrics
            input_tokens = self._get_cloudwatch_metric(
                'AWS/Bedrock', 'InputTokens', start_time, end_time, 'Sum'
            )
            metrics['total_input_tokens'] = sum(point['Sum'] for point in input_tokens)
            
            output_tokens = self._get_cloudwatch_metric(
                'AWS/Bedrock', 'OutputTokens', start_time, end_time, 'Sum'
            )
            metrics['total_output_tokens'] = sum(point['Sum'] for point in output_tokens)
            
            # Get duration metrics
            duration = self._get_cloudwatch_metric(
                'AWS/Bedrock', 'Duration', start_time, end_time, 'Average'
            )
            if duration:
                metrics['avg_duration'] = statistics.mean(point['Average'] for point in duration)
            
            # Calculate success rate
            if metrics['total_invocations'] > 0:
                metrics['success_rate'] = (
                    (metrics['total_invocations'] - metrics['total_errors']) / 
                    metrics['total_invocations'] * 100
                )
            else:
                metrics['success_rate'] = 0
                
        except Exception as e:
            logger.error(f"Error collecting usage metrics: {str(e)}")
            
        return metrics
    
    def _get_cloudwatch_metric(
        self, 
        namespace: str, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime, 
        statistic: str
    ) -> List[Dict[str, Any]]:
        """
        Get CloudWatch metric data
        
        Args:
            namespace: CloudWatch namespace
            metric_name: Name of the metric
            start_time: Start time for metrics
            end_time: End time for metrics
            statistic: Statistic to retrieve (Sum, Average, etc.)
            
        Returns:
            List of metric data points
        """
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=[statistic]
            )
            return response.get('Datapoints', [])
        except Exception as e:
            logger.error(f"Error getting CloudWatch metric {metric_name}: {str(e)}")
            return []
    
    def analyze_user_behavior(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Analyze user behavior patterns from CloudTrail logs
        
        Args:
            hours_back: Number of hours to look back for analysis
            
        Returns:
            Dictionary containing user behavior analysis
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        log_group_name = f'/aws/bedrock/application-logs/{self.environment}'
        
        query = """
        fields @timestamp, userIdentity.userName, eventName, sourceIPAddress, requestParameters.modelId
        | filter eventName like /Bedrock/
        | stats count() as requestCount by userIdentity.userName, requestParameters.modelId
        | sort requestCount desc
        """
        
        try:
            # Start CloudWatch Insights query
            response = self.logs_client.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query
            )
            
            query_id = response['queryId']
            
            # Wait for query completion and get results
            import time
            while True:
                time.sleep(2)
                result = self.logs_client.get_query_results(queryId=query_id)
                if result['status'] == 'Complete':
                    break
                elif result['status'] == 'Failed':
                    logger.error("CloudWatch Insights query failed")
                    return {}
            
            # Process results
            user_behavior = {
                'top_users': [],
                'model_preferences': defaultdict(int),
                'unique_users': set(),
                'total_requests': 0
            }
            
            for result_row in result['results']:
                row_data = {item['field']: item['value'] for item in result_row}
                user_behavior['top_users'].append(row_data)
                user_behavior['unique_users'].add(row_data.get('userIdentity.userName', 'unknown'))
                user_behavior['model_preferences'][row_data.get('requestParameters.modelId', 'unknown')] += int(row_data.get('requestCount', 0))
                user_behavior['total_requests'] += int(row_data.get('requestCount', 0))
            
            user_behavior['unique_users'] = len(user_behavior['unique_users'])
            
            return user_behavior
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            return {}
    
    def detect_anomalies(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in Bedrock usage patterns
        
        Args:
            threshold_multiplier: Multiplier for standard deviation to detect anomalies
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Get last 7 days of data for baseline
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            # Collect baseline metrics
            baseline_metrics = []
            current_time = start_time
            while current_time < end_time:
                next_time = current_time + timedelta(hours=1)
                hourly_metrics = self.collect_usage_metrics(current_time, next_time)
                baseline_metrics.append(hourly_metrics['total_invocations'])
                current_time = next_time
            
            if len(baseline_metrics) < 24:  # Need at least 24 hours of data
                logger.warning("Insufficient data for anomaly detection")
                return anomalies
            
            # Calculate baseline statistics
            baseline_mean = statistics.mean(baseline_metrics)
            baseline_stdev = statistics.stdev(baseline_metrics)
            threshold = baseline_mean + (threshold_multiplier * baseline_stdev)
            
            # Check current hour against baseline
            current_hour_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            current_hour_end = current_hour_start + timedelta(hours=1)
            current_metrics = self.collect_usage_metrics(current_hour_start, current_hour_end)
            
            if current_metrics['total_invocations'] > threshold:
                anomalies.append({
                    'type': 'high_usage',
                    'current_value': current_metrics['total_invocations'],
                    'threshold': threshold,
                    'baseline_mean': baseline_mean,
                    'timestamp': current_hour_start.isoformat(),
                    'severity': 'high' if current_metrics['total_invocations'] > threshold * 1.5 else 'medium'
                })
            
            # Check error rate anomalies
            if current_metrics['total_invocations'] > 0:
                current_error_rate = (current_metrics['total_errors'] / current_metrics['total_invocations']) * 100
                baseline_error_rates = []
                
                # Calculate baseline error rates
                current_time = start_time
                while current_time < end_time - timedelta(hours=1):
                    next_time = current_time + timedelta(hours=1)
                    hourly_metrics = self.collect_usage_metrics(current_time, next_time)
                    if hourly_metrics['total_invocations'] > 0:
                        error_rate = (hourly_metrics['total_errors'] / hourly_metrics['total_invocations']) * 100
                        baseline_error_rates.append(error_rate)
                    current_time = next_time
                
                if baseline_error_rates:
                    baseline_error_mean = statistics.mean(baseline_error_rates)
                    baseline_error_stdev = statistics.stdev(baseline_error_rates) if len(baseline_error_rates) > 1 else 0
                    error_threshold = baseline_error_mean + (threshold_multiplier * baseline_error_stdev)
                    
                    if current_error_rate > error_threshold and current_error_rate > 5:  # At least 5% error rate
                        anomalies.append({
                            'type': 'high_error_rate',
                            'current_value': current_error_rate,
                            'threshold': error_threshold,
                            'baseline_mean': baseline_error_mean,
                            'timestamp': current_hour_start.isoformat(),
                            'severity': 'high' if current_error_rate > error_threshold * 1.5 else 'medium'
                        })
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
        
        return anomalies
    
    def generate_cost_analysis(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Generate cost analysis based on token usage
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing cost analysis
        """
        # Model pricing (tokens per dollar) - these are example rates
        model_pricing = {
            'anthropic.claude-v2': {'input': 0.00001102, 'output': 0.00003268},  # per token
            'amazon.titan-text-express-v1': {'input': 0.0000008, 'output': 0.0000016},
            'ai21.j2-ultra-v1': {'input': 0.000015, 'output': 0.000015},
            'cohere.command-text-v14': {'input': 0.000015, 'output': 0.000015}
        }
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        cost_analysis = {
            'total_estimated_cost': 0,
            'cost_by_model': defaultdict(float),
            'cost_by_day': defaultdict(float),
            'token_usage': {
                'input_tokens': 0,
                'output_tokens': 0
            }
        }
        
        try:
            # Get token usage metrics
            metrics = self.collect_usage_metrics(start_time, end_time)
            cost_analysis['token_usage']['input_tokens'] = metrics['total_input_tokens']
            cost_analysis['token_usage']['output_tokens'] = metrics['total_output_tokens']
            
            # Calculate estimated costs (simplified - would need more detailed breakdown by model)
            # This is a simplified calculation assuming average model pricing
            avg_input_price = statistics.mean([pricing['input'] for pricing in model_pricing.values()])
            avg_output_price = statistics.mean([pricing['output'] for pricing in model_pricing.values()])
            
            input_cost = metrics['total_input_tokens'] * avg_input_price
            output_cost = metrics['total_output_tokens'] * avg_output_price
            
            cost_analysis['total_estimated_cost'] = input_cost + output_cost
            cost_analysis['input_token_cost'] = input_cost
            cost_analysis['output_token_cost'] = output_cost
            
        except Exception as e:
            logger.error(f"Error generating cost analysis: {str(e)}")
        
        return cost_analysis
    
    def send_alert(self, message: str, subject: str = "Bedrock Monitoring Alert") -> bool:
        """
        Send alert via SNS
        
        Args:
            message: Alert message
            subject: Alert subject
            
        Returns:
            True if alert sent successfully, False otherwise
        """
        if not self.sns_topic_arn:
            logger.warning("SNS topic ARN not configured, cannot send alert")
            return False
        
        try:
            self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Message=message,
                Subject=subject
            )
            logger.info(f"Alert sent successfully: {subject}")
            return True
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False
    
    def publish_custom_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Publish custom metrics to CloudWatch
        
        Args:
            metrics: Dictionary of metrics to publish
            
        Returns:
            True if metrics published successfully, False otherwise
        """
        try:
            metric_data = []
            
            # Prepare metric data for CloudWatch
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_data.append({
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': 'Count',
                        'Dimensions': [
                            {
                                'Name': 'Environment',
                                'Value': self.environment
                            }
                        ]
                    })
            
            # Publish metrics in batches of 20 (CloudWatch limit)
            for i in range(0, len(metric_data), 20):
                batch = metric_data[i:i+20]
                self.cloudwatch_client.put_metric_data(
                    Namespace='Custom/Bedrock',
                    MetricData=batch
                )
            
            logger.info(f"Published {len(metric_data)} custom metrics to CloudWatch")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing custom metrics: {str(e)}")
            return False

def lambda_handler(event, context):
    """
    AWS Lambda handler for scheduled monitoring
    """
    try:
        monitor = BedrockMonitor()
        
        # Collect current metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        metrics = monitor.collect_usage_metrics(start_time, end_time)
        
        # Publish custom metrics
        monitor.publish_custom_metrics(metrics)
        
        # Check for anomalies
        anomalies = monitor.detect_anomalies()
        
        if anomalies:
            alert_message = f"Detected {len(anomalies)} anomalies in Bedrock usage:\n\n"
            for anomaly in anomalies:
                alert_message += f"- {anomaly['type']}: Current value {anomaly['current_value']}, "
                alert_message += f"Threshold: {anomaly['threshold']:.2f}, Severity: {anomaly['severity']}\n"
            
            monitor.send_alert(alert_message, "Bedrock Usage Anomaly Detected")
        
        # Analyze user behavior
        user_behavior = monitor.analyze_user_behavior()
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Monitoring completed successfully',
                'metrics_collected': len(metrics),
                'anomalies_detected': len(anomalies),
                'unique_users': user_behavior.get('unique_users', 0)
            })
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

if __name__ == "__main__":
    # For local testing
    monitor = BedrockMonitor()
    
    # Test metric collection
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    metrics = monitor.collect_usage_metrics(start_time, end_time)
    
    print("Collected Metrics:")
    print(json.dumps(metrics, indent=2, default=str))
    
    # Test anomaly detection
    anomalies = monitor.detect_anomalies()
    print(f"\nDetected {len(anomalies)} anomalies")
    
    # Test cost analysis
    cost_analysis = monitor.generate_cost_analysis()
    print("\nCost Analysis:")
    print(json.dumps(cost_analysis, indent=2, default=str))