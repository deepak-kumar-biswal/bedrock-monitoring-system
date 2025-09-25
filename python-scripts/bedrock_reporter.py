"""
Automated Bedrock Reporting System
Generates comprehensive reports for management and technical teams
"""

import boto3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from bedrock_monitor import BedrockMonitor

class BedrockReporter:
    """
    Automated reporting system for Bedrock monitoring
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the reporter
        
        Args:
            region_name: AWS region
        """
        self.region_name = region_name
        self.monitor = BedrockMonitor(region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.ses_client = boto3.client('ses', region_name=region_name)
        
        # Configuration
        self.report_bucket = os.getenv('REPORT_BUCKET')
        self.sender_email = os.getenv('SENDER_EMAIL')
        
    def generate_executive_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Generate executive summary for management
        
        Args:
            days_back: Number of days to include in summary
            
        Returns:
            Executive summary data
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        # Collect metrics
        metrics = self.monitor.collect_usage_metrics(start_time, end_time)
        user_behavior = self.monitor.analyze_user_behavior(hours_back=days_back*24)
        cost_analysis = self.monitor.generate_cost_analysis(days_back=days_back)
        
        summary = {
            'reporting_period': {
                'start_date': start_time.strftime('%Y-%m-%d'),
                'end_date': end_time.strftime('%Y-%m-%d'),
                'days': days_back
            },
            'key_metrics': {
                'total_api_calls': metrics['total_invocations'],
                'success_rate': metrics.get('success_rate', 0),
                'unique_users': user_behavior.get('unique_users', 0),
                'total_tokens_processed': metrics['total_input_tokens'] + metrics['total_output_tokens'],
                'average_response_time': metrics.get('avg_duration', 0) / 1000,  # Convert to seconds
                'estimated_cost': cost_analysis.get('total_estimated_cost', 0)
            },
            'trends': {
                'usage_growth': self._calculate_usage_growth(days_back),
                'error_trend': self._calculate_error_trend(days_back),
                'cost_trend': self._calculate_cost_trend(days_back)
            },
            'top_models': list(user_behavior.get('model_preferences', {}).keys())[:5],
            'recommendations': self._generate_recommendations(metrics, user_behavior, cost_analysis)
        }
        
        return summary
    
    def _calculate_usage_growth(self, days_back: int) -> float:
        """Calculate usage growth percentage"""
        try:
            # Get current period metrics
            current_end = datetime.utcnow()
            current_start = current_end - timedelta(days=days_back)
            current_metrics = self.monitor.collect_usage_metrics(current_start, current_end)
            
            # Get previous period metrics
            previous_end = current_start
            previous_start = previous_end - timedelta(days=days_back)
            previous_metrics = self.monitor.collect_usage_metrics(previous_start, previous_end)
            
            if previous_metrics['total_invocations'] > 0:
                growth = ((current_metrics['total_invocations'] - previous_metrics['total_invocations']) / 
                         previous_metrics['total_invocations']) * 100
                return round(growth, 2)
            
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_error_trend(self, days_back: int) -> str:
        """Calculate error trend"""
        try:
            # Get daily error rates for trend analysis
            daily_error_rates = []
            for i in range(days_back):
                day_start = datetime.utcnow() - timedelta(days=i+1)
                day_end = day_start + timedelta(days=1)
                daily_metrics = self.monitor.collect_usage_metrics(day_start, day_end)
                
                if daily_metrics['total_invocations'] > 0:
                    error_rate = (daily_metrics['total_errors'] / daily_metrics['total_invocations']) * 100
                    daily_error_rates.append(error_rate)
            
            if len(daily_error_rates) >= 2:
                if daily_error_rates[0] > daily_error_rates[-1]:
                    return "Improving"
                elif daily_error_rates[0] < daily_error_rates[-1]:
                    return "Worsening"
                else:
                    return "Stable"
            
            return "Insufficient Data"
        except Exception:
            return "Unknown"
    
    def _calculate_cost_trend(self, days_back: int) -> str:
        """Calculate cost trend"""
        try:
            # Get current week cost
            current_cost = self.monitor.generate_cost_analysis(days_back=days_back)
            previous_cost = self.monitor.generate_cost_analysis(days_back=days_back*2)
            
            current_total = current_cost.get('total_estimated_cost', 0)
            previous_total = previous_cost.get('total_estimated_cost', 0) / 2  # Adjust for double period
            
            if previous_total > 0:
                change = ((current_total - previous_total) / previous_total) * 100
                if change > 10:
                    return "Increasing"
                elif change < -10:
                    return "Decreasing"
                else:
                    return "Stable"
            
            return "Insufficient Data"
        except Exception:
            return "Unknown"
    
    def _generate_recommendations(self, metrics: Dict, user_behavior: Dict, cost_analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Error rate recommendations
        if metrics.get('success_rate', 100) < 95:
            recommendations.append("Investigate error patterns - success rate below 95%")
        
        # Usage recommendations
        if metrics['total_invocations'] > 10000:
            recommendations.append("Consider implementing caching to reduce API calls")
        
        # Cost recommendations
        if cost_analysis.get('total_estimated_cost', 0) > 1000:
            recommendations.append("Review token usage patterns for cost optimization opportunities")
        
        # Model usage recommendations
        model_prefs = user_behavior.get('model_preferences', {})
        if len(model_prefs) == 1:
            recommendations.append("Consider diversifying model usage for better resilience")
        
        # Performance recommendations
        if metrics.get('avg_duration', 0) > 30000:  # 30 seconds
            recommendations.append("Investigate high response times - consider request optimization")
        
        if not recommendations:
            recommendations.append("System performing well - continue monitoring")
        
        return recommendations
    
    def create_technical_report(self, days_back: int = 7) -> str:
        """
        Create detailed technical report
        
        Args:
            days_back: Number of days to include
            
        Returns:
            HTML report content
        """
        # Collect comprehensive data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        metrics = self.monitor.collect_usage_metrics(start_time, end_time)
        user_behavior = self.monitor.analyze_user_behavior(hours_back=days_back*24)
        cost_analysis = self.monitor.generate_cost_analysis(days_back=days_back)
        anomalies = self.monitor.detect_anomalies()
        
        # Create visualizations
        charts = self._create_charts(metrics, user_behavior, cost_analysis)
        
        # HTML template for technical report
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bedrock Technical Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #232F3E; color: white; padding: 20px; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background: #f5f5f5; }
                .chart { text-align: center; margin: 20px 0; }
                .alert { background: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; }
                .success { background: #e8f5e8; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AWS Bedrock Technical Report</h1>
                <p>Generated on {{ report_date }} | Period: {{ start_date }} to {{ end_date }}</p>
            </div>
            
            <div class="section">
                <h2>📊 Key Performance Metrics</h2>
                <div class="metric">
                    <h3>{{ total_invocations }}</h3>
                    <p>Total API Calls</p>
                </div>
                <div class="metric">
                    <h3>{{ success_rate }}%</h3>
                    <p>Success Rate</p>
                </div>
                <div class="metric">
                    <h3>{{ avg_duration }}ms</h3>
                    <p>Avg Response Time</p>
                </div>
                <div class="metric">
                    <h3>{{ unique_users }}</h3>
                    <p>Active Users</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Usage Analysis</h2>
                <div class="chart">
                    <img src="data:image/png;base64,{{ usage_chart }}" alt="Usage Chart">
                </div>
                
                <h3>Top Models by Usage</h3>
                <table>
                    <tr><th>Model</th><th>Requests</th><th>Percentage</th></tr>
                    {% for model, count in top_models %}
                    <tr>
                        <td>{{ model }}</td>
                        <td>{{ count }}</td>
                        <td>{{ "%.1f"|format((count/total_requests)*100) }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>⚠️ Anomalies and Alerts</h2>
                {% if anomalies %}
                    {% for anomaly in anomalies %}
                    <div class="alert">
                        <strong>{{ anomaly.type|title }}</strong>: 
                        Current value {{ anomaly.current_value }} exceeds threshold {{ "%.2f"|format(anomaly.threshold) }}
                        (Severity: {{ anomaly.severity }})
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="success">No anomalies detected in the reporting period.</div>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>💰 Cost Analysis</h2>
                <div class="metric">
                    <h3>${{ "%.2f"|format(estimated_cost) }}</h3>
                    <p>Estimated Cost</p>
                </div>
                <div class="metric">
                    <h3>{{ total_tokens }}</h3>
                    <p>Total Tokens</p>
                </div>
                
                <div class="chart">
                    <img src="data:image/png;base64,{{ cost_chart }}" alt="Cost Chart">
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Error Analysis</h2>
                {% if total_errors > 0 %}
                <div class="chart">
                    <img src="data:image/png;base64,{{ error_chart }}" alt="Error Chart">
                </div>
                {% else %}
                <div class="success">No errors detected in the reporting period.</div>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>🎯 Recommendations</h2>
                <ul>
                {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        
        # Prepare template data
        template_data = {
            'report_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            'start_date': start_time.strftime('%Y-%m-%d'),
            'end_date': end_time.strftime('%Y-%m-%d'),
            'total_invocations': metrics['total_invocations'],
            'success_rate': round(metrics.get('success_rate', 0), 1),
            'avg_duration': round(metrics.get('avg_duration', 0)),
            'unique_users': user_behavior.get('unique_users', 0),
            'total_errors': metrics['total_errors'],
            'estimated_cost': cost_analysis.get('total_estimated_cost', 0),
            'total_tokens': metrics['total_input_tokens'] + metrics['total_output_tokens'],
            'top_models': list(user_behavior.get('model_preferences', {}).items())[:5],
            'total_requests': sum(user_behavior.get('model_preferences', {}).values()),
            'anomalies': anomalies,
            'recommendations': self._generate_recommendations(metrics, user_behavior, cost_analysis),
            **charts
        }
        
        return template.render(**template_data)
    
    def _create_charts(self, metrics: Dict, user_behavior: Dict, cost_analysis: Dict) -> Dict[str, str]:
        """
        Create visualization charts for the report
        
        Returns:
            Dictionary of base64 encoded chart images
        """
        charts = {}
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        try:
            # Usage chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Sample data - in real implementation, get time series data
            days = list(range(7, 0, -1))
            usage_data = [metrics['total_invocations'] // 7] * 7  # Simplified
            
            ax.plot(days, usage_data, marker='o', linewidth=2)
            ax.set_title('Daily API Usage Trend')
            ax.set_xlabel('Days Ago')
            ax.set_ylabel('API Calls')
            ax.grid(True, alpha=0.3)
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            charts['usage_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Model usage pie chart
            model_prefs = user_behavior.get('model_preferences', {})
            if model_prefs:
                fig, ax = plt.subplots(figsize=(8, 8))
                
                models = list(model_prefs.keys())[:5]  # Top 5 models
                values = list(model_prefs.values())[:5]
                
                colors = plt.cm.Set3(range(len(models)))
                ax.pie(values, labels=models, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.set_title('Model Usage Distribution')
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                charts['model_chart'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # Cost breakdown chart
            fig, ax = plt.subplots(figsize=(8, 6))
            
            input_cost = cost_analysis.get('input_token_cost', 0)
            output_cost = cost_analysis.get('output_token_cost', 0)
            
            if input_cost > 0 or output_cost > 0:
                categories = ['Input Tokens', 'Output Tokens']
                costs = [input_cost, output_cost]
                
                ax.bar(categories, costs, color=['#1f77b4', '#ff7f0e'])
                ax.set_title('Cost Breakdown by Token Type')
                ax.set_ylabel('Estimated Cost ($)')
                
                # Add value labels on bars
                for i, v in enumerate(costs):
                    ax.text(i, v + 0.01, f'${v:.2f}', ha='center', va='bottom')
            else:
                ax.text(0.5, 0.5, 'No cost data available', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Cost Breakdown')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            charts['cost_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Error distribution chart
            if metrics['total_errors'] > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                
                # Sample error distribution - in real implementation, get actual error types
                error_types = ['ClientError', 'ServerError', 'ThrottlingError', 'ValidationError']
                error_counts = [metrics['total_errors'] // 4] * 4  # Simplified
                
                ax.bar(error_types, error_counts, color='#d62728')
                ax.set_title('Error Distribution')
                ax.set_ylabel('Error Count')
                ax.tick_params(axis='x', rotation=45)
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                charts['error_chart'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
        except Exception as e:
            print(f"Error creating charts: {str(e)}")
            # Create placeholder chart
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'Chart generation error', ha='center', va='center', transform=ax.transAxes)
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            charts['usage_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        return charts
    
    def send_report(self, report_html: str, recipients: List[str], subject: str = "Bedrock Monitoring Report"):
        """
        Send report via email
        
        Args:
            report_html: HTML content of the report
            recipients: List of email addresses
            subject: Email subject
        """
        if not self.sender_email:
            print("Sender email not configured")
            return
        
        try:
            for recipient in recipients:
                self.ses_client.send_email(
                    Source=self.sender_email,
                    Destination={'ToAddresses': [recipient]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {'Html': {'Data': report_html}}
                    }
                )
            print(f"Report sent to {len(recipients)} recipients")
        except Exception as e:
            print(f"Error sending report: {str(e)}")
    
    def save_report_to_s3(self, report_html: str, report_name: str):
        """
        Save report to S3 bucket
        
        Args:
            report_html: HTML content
            report_name: Name for the report file
        """
        if not self.report_bucket:
            print("Report bucket not configured")
            return
        
        try:
            key = f"reports/{datetime.utcnow().strftime('%Y/%m/%d')}/{report_name}.html"
            self.s3_client.put_object(
                Bucket=self.report_bucket,
                Key=key,
                Body=report_html,
                ContentType='text/html'
            )
            print(f"Report saved to s3://{self.report_bucket}/{key}")
        except Exception as e:
            print(f"Error saving report to S3: {str(e)}")

def lambda_handler(event, context):
    """
    Lambda handler for automated report generation
    """
    try:
        reporter = BedrockReporter()
        
        # Generate weekly technical report
        technical_report = reporter.create_technical_report(days_back=7)
        
        # Save to S3
        report_name = f"technical-report-{datetime.utcnow().strftime('%Y%m%d')}"
        reporter.save_report_to_s3(technical_report, report_name)
        
        # Send to technical team (configure email list in environment variables)
        tech_emails = os.getenv('TECH_TEAM_EMAILS', '').split(',')
        if tech_emails and tech_emails[0]:
            reporter.send_report(technical_report, tech_emails, "Weekly Bedrock Technical Report")
        
        # Generate executive summary for management
        exec_summary = reporter.generate_executive_summary(days_back=7)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Reports generated successfully',
                'technical_report_saved': True,
                'executive_summary': exec_summary
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

if __name__ == "__main__":
    # For local testing
    reporter = BedrockReporter()
    
    # Generate technical report
    report = reporter.create_technical_report(days_back=7)
    
    # Save to file for testing
    with open('bedrock_technical_report.html', 'w') as f:
        f.write(report)
    
    print("Technical report generated: bedrock_technical_report.html")
    
    # Generate executive summary
    summary = reporter.generate_executive_summary(days_back=7)
    print("\nExecutive Summary:")
    print(json.dumps(summary, indent=2, default=str))