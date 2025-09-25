"""
AWS Bedrock Monitoring Architecture Diagram Generator
Creates a visual representation of the monitoring solution architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    """
    Create a comprehensive architecture diagram for the Bedrock monitoring solution
    """
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Define colors
    colors = {
        'aws_orange': '#FF9900',
        'aws_blue': '#232F3E',
        'light_blue': '#5294CF',
        'green': '#4CAF50',
        'red': '#F44336',
        'purple': '#9C27B0',
        'gray': '#9E9E9E',
        'light_gray': '#F5F5F5'
    }
    
    # Title
    ax.text(10, 13.5, 'AWS Bedrock Comprehensive Monitoring Architecture', 
            fontsize=24, fontweight='bold', ha='center', color=colors['aws_blue'])
    
    # Define component positions and sizes
    components = {
        # Applications Layer
        'web_app': {'pos': (1, 11), 'size': (2, 1), 'label': 'Web\nApplications'},
        'mobile_app': {'pos': (4, 11), 'size': (2, 1), 'label': 'Mobile\nApplications'},
        'api_clients': {'pos': (7, 11), 'size': (2, 1), 'label': 'API\nClients'},
        
        # AWS Bedrock Services
        'bedrock_runtime': {'pos': (2, 9), 'size': (3, 1), 'label': 'AWS Bedrock\nRuntime API'},
        'bedrock_models': {'pos': (6, 9), 'size': (3, 1), 'label': 'Bedrock Foundation\nModels'},
        
        # Monitoring Infrastructure
        'cloudtrail': {'pos': (1, 7), 'size': (2.5, 1), 'label': 'AWS CloudTrail\n(API Logging)'},
        'cloudwatch': {'pos': (4.5, 7), 'size': (2.5, 1), 'label': 'Amazon CloudWatch\n(Metrics & Logs)'},
        'lambda_monitor': {'pos': (8, 7), 'size': (2.5, 1), 'label': 'Lambda Functions\n(Custom Metrics)'},
        
        # Storage
        's3_logs': {'pos': (1, 5), 'size': (2, 1), 'label': 'S3 Bucket\n(Log Storage)'},
        'log_groups': {'pos': (4, 5), 'size': (2, 1), 'label': 'CloudWatch\nLog Groups'},
        's3_reports': {'pos': (7, 5), 'size': (2, 1), 'label': 'S3 Bucket\n(Reports)'},
        
        # Analytics & Reporting
        'log_insights': {'pos': (1, 3), 'size': (2.5, 1), 'label': 'CloudWatch\nLog Insights'},
        'custom_analytics': {'pos': (4.5, 3), 'size': (2.5, 1), 'label': 'Custom Analytics\n(Python Scripts)'},
        'automated_reports': {'pos': (8, 3), 'size': (2.5, 1), 'label': 'Automated\nReporting'},
        
        # Dashboards
        'tech_dashboard': {'pos': (12, 9), 'size': (2.5, 1), 'label': 'Technical\nDashboard'},
        'mgmt_dashboard': {'pos': (15.5, 9), 'size': (2.5, 1), 'label': 'Management\nDashboard'},
        'security_dashboard': {'pos': (12, 7), 'size': (2.5, 1), 'label': 'Security\nDashboard'},
        'cost_dashboard': {'pos': (15.5, 7), 'size': (2.5, 1), 'label': 'Cost & Usage\nDashboard'},
        
        # Alerting
        'sns': {'pos': (12, 5), 'size': (2, 1), 'label': 'Amazon SNS\n(Alerts)'},
        'ses': {'pos': (15, 5), 'size': (2, 1), 'label': 'Amazon SES\n(Email Reports)'},
        
        # External Systems
        'stakeholders': {'pos': (14, 3), 'size': (3, 1), 'label': 'Stakeholders\n(Email Recipients)'},
        'eventbridge': {'pos': (11, 3), 'size': (2, 1), 'label': 'EventBridge\n(Scheduling)'}
    }
    
    # Draw components
    for comp_name, comp_data in components.items():
        x, y = comp_data['pos']
        width, height = comp_data['size']
        label = comp_data['label']
        
        # Determine color based on component type
        if 'bedrock' in comp_name.lower():
            color = colors['aws_orange']
        elif any(service in comp_name.lower() for service in ['cloudwatch', 'cloudtrail', 'lambda', 's3', 'sns', 'ses']):
            color = colors['light_blue']
        elif 'dashboard' in comp_name.lower():
            color = colors['green']
        elif comp_name in ['web_app', 'mobile_app', 'api_clients']:
            color = colors['purple']
        elif 'analytics' in comp_name.lower() or 'insights' in comp_name.lower():
            color = colors['gray']
        else:
            color = colors['light_gray']
        
        # Draw component box
        rect = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor=colors['aws_blue'],
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        # Add label
        ax.text(x + width/2, y + height/2, label, 
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white' if color in [colors['aws_orange'], colors['aws_blue'], colors['purple']] else 'black')
    
    # Define connections (arrows)
    connections = [
        # Applications to Bedrock
        ('web_app', 'bedrock_runtime'),
        ('mobile_app', 'bedrock_runtime'),
        ('api_clients', 'bedrock_models'),
        
        # Bedrock to Monitoring
        ('bedrock_runtime', 'cloudtrail'),
        ('bedrock_runtime', 'cloudwatch'),
        ('bedrock_models', 'cloudwatch'),
        ('bedrock_models', 'lambda_monitor'),
        
        # Monitoring to Storage
        ('cloudtrail', 's3_logs'),
        ('cloudwatch', 'log_groups'),
        ('lambda_monitor', 's3_reports'),
        
        # Storage to Analytics
        ('s3_logs', 'log_insights'),
        ('log_groups', 'custom_analytics'),
        ('s3_reports', 'automated_reports'),
        
        # Analytics to Dashboards
        ('cloudwatch', 'tech_dashboard'),
        ('cloudwatch', 'mgmt_dashboard'),
        ('cloudwatch', 'security_dashboard'),
        ('cloudwatch', 'cost_dashboard'),
        
        # Monitoring to Alerting
        ('lambda_monitor', 'sns'),
        ('automated_reports', 'ses'),
        
        # Alerting to External
        ('sns', 'stakeholders'),
        ('ses', 'stakeholders'),
        
        # Scheduling
        ('eventbridge', 'lambda_monitor'),
        ('eventbridge', 'automated_reports')
    ]
    
    # Draw connections
    for start_comp, end_comp in connections:
        start_pos = components[start_comp]['pos']
        start_size = components[start_comp]['size']
        end_pos = components[end_comp]['pos']
        end_size = components[end_comp]['size']
        
        # Calculate connection points
        start_x = start_pos[0] + start_size[0]/2
        start_y = start_pos[1]
        end_x = end_pos[0] + end_size[0]/2
        end_y = end_pos[1] + end_size[1]
        
        # Adjust connection points based on positions
        if start_y > end_y:  # Arrow going down
            start_y = start_pos[1]
            end_y = end_pos[1] + end_size[1]
        else:  # Arrow going up
            start_y = start_pos[1] + start_size[1]
            end_y = end_pos[1]
        
        # If components are side by side, connect horizontally
        if abs(start_y - end_y) < 1:
            if start_x < end_x:  # Arrow going right
                start_x = start_pos[0] + start_size[0]
                start_y = start_pos[1] + start_size[1]/2
                end_x = end_pos[0]
                end_y = end_pos[1] + end_size[1]/2
            else:  # Arrow going left
                start_x = start_pos[0]
                start_y = start_pos[1] + start_size[1]/2
                end_x = end_pos[0] + end_size[0]
                end_y = end_pos[1] + end_size[1]/2
        
        # Draw arrow
        arrow = patches.FancyArrowPatch(
            (start_x, start_y), (end_x, end_y),
            arrowstyle='->', mutation_scale=20,
            color=colors['aws_blue'], linewidth=2, alpha=0.7
        )
        ax.add_patch(arrow)
    
    # Add layer labels
    layer_labels = [
        {'pos': (0.2, 11.5), 'text': 'Application\nLayer', 'color': colors['purple']},
        {'pos': (0.2, 9.5), 'text': 'Bedrock\nServices', 'color': colors['aws_orange']},
        {'pos': (0.2, 7.5), 'text': 'Monitoring\nInfrastructure', 'color': colors['light_blue']},
        {'pos': (0.2, 5.5), 'text': 'Storage\nLayer', 'color': colors['gray']},
        {'pos': (0.2, 3.5), 'text': 'Analytics &\nReporting', 'color': colors['gray']},
    ]
    
    for layer in layer_labels:
        ax.text(layer['pos'][0], layer['pos'][1], layer['text'], 
                fontsize=12, fontweight='bold', ha='left', va='center',
                color=layer['color'], rotation=90)
    
    # Add key metrics boxes
    metrics_box = FancyBboxPatch(
        (11.5, 11), 7, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['light_gray'],
        edgecolor=colors['aws_blue'],
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(metrics_box)
    
    metrics_text = """Key Monitoring Metrics:
    • API Invocations & Success Rate  • Token Usage & Cost Analysis
    • Response Times & Performance   • User Behavior & Access Patterns
    • Error Rates & Types           • Security Events & Anomalies"""
    
    ax.text(15, 11.75, metrics_text, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add data flow legend
    legend_box = FancyBboxPatch(
        (11.5, 0.5), 7, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['light_gray'],
        edgecolor=colors['aws_blue'],
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(legend_box)
    
    legend_text = """Data Flow Types:
    🔄 Real-time Metrics    📊 Log Aggregation    📈 Batch Analytics
    🚨 Alert Notifications  📧 Scheduled Reports  🔍 On-demand Queries"""
    
    ax.text(15, 1.25, legend_text, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add compliance note
    ax.text(10, 0.2, 'Architecture follows AWS Well-Architected Framework principles for Security, Reliability, Performance, and Cost Optimization',
            ha='center', va='center', fontsize=10, style='italic', color=colors['aws_blue'])
    
    plt.tight_layout()
    plt.savefig('bedrock_monitoring_architecture.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('bedrock_monitoring_architecture.pdf', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    return fig

def create_data_flow_diagram():
    """
    Create a detailed data flow diagram
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    colors = {
        'data': '#4CAF50',
        'process': '#2196F3',
        'storage': '#FF9800',
        'output': '#9C27B0'
    }
    
    # Title
    ax.text(8, 11.5, 'Bedrock Monitoring Data Flow', 
            fontsize=20, fontweight='bold', ha='center')
    
    # Data flow stages
    stages = [
        {'pos': (1, 9), 'size': (2.5, 1.5), 'label': '1. Data Collection\n• API Calls\n• CloudTrail Events\n• Custom Metrics', 'color': colors['data']},
        {'pos': (5, 9), 'size': (2.5, 1.5), 'label': '2. Data Processing\n• Log Parsing\n• Metric Aggregation\n• Anomaly Detection', 'color': colors['process']},
        {'pos': (9, 9), 'size': (2.5, 1.5), 'label': '3. Data Storage\n• S3 (Long-term)\n• CloudWatch\n• Log Groups', 'color': colors['storage']},
        {'pos': (13, 9), 'size': (2.5, 1.5), 'label': '4. Data Output\n• Dashboards\n• Reports\n• Alerts', 'color': colors['output']},
        
        {'pos': (1, 6), 'size': (2.5, 1.5), 'label': '5. Real-time\nMonitoring\n• Live Metrics\n• Instant Alerts', 'color': colors['process']},
        {'pos': (5, 6), 'size': (2.5, 1.5), 'label': '6. Batch Analytics\n• Daily Reports\n• Trend Analysis\n• Cost Analysis', 'color': colors['process']},
        {'pos': (9, 6), 'size': (2.5, 1.5), 'label': '7. User Behavior\nAnalysis\n• Usage Patterns\n• Security Events', 'color': colors['process']},
        {'pos': (13, 6), 'size': (2.5, 1.5), 'label': '8. Automated\nActions\n• Scaling\n• Notifications', 'color': colors['output']},
        
        {'pos': (3, 3), 'size': (3, 1.5), 'label': '9. Management\nReporting\n• Executive Summary\n• KPI Dashboard', 'color': colors['output']},
        {'pos': (10, 3), 'size': (3, 1.5), 'label': '10. Technical\nReporting\n• Performance Metrics\n• Error Analysis', 'color': colors['output']},
    ]
    
    # Draw stages
    for stage in stages:
        x, y = stage['pos']
        width, height = stage['size']
        
        rect = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.1",
            facecolor=stage['color'],
            edgecolor='black',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        ax.text(x + width/2, y + height/2, stage['label'], 
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white')
    
    # Draw flow arrows
    flow_arrows = [
        ((2.25, 9), (5, 9.75)),
        ((7.5, 9.75), (9, 9.75)),
        ((11.5, 9.75), (13, 9.75)),
        ((2.25, 9), (2.25, 7.5)),
        ((2.25, 6), (5, 6.75)),
        ((7.5, 6.75), (9, 6.75)),
        ((11.5, 6.75), (13, 6.75)),
        ((4.5, 6), (4.5, 4.5)),
        ((11.5, 6), (11.5, 4.5))
    ]
    
    for start, end in flow_arrows:
        arrow = patches.FancyArrowPatch(
            start, end,
            arrowstyle='->', mutation_scale=20,
            color='black', linewidth=2
        )
        ax.add_patch(arrow)
    
    # Add timing information
    ax.text(8, 1, 'Data Processing Timeline: Real-time (< 5 min) • Near real-time (5-15 min) • Batch (Daily/Weekly)',
            ha='center', va='center', fontsize=12, style='italic')
    
    plt.tight_layout()
    plt.savefig('bedrock_data_flow.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    return fig

if __name__ == "__main__":
    print("Generating architecture diagrams...")
    
    # Create main architecture diagram
    arch_fig = create_architecture_diagram()
    print("✅ Architecture diagram saved as: bedrock_monitoring_architecture.png/.pdf")
    
    # Create data flow diagram
    flow_fig = create_data_flow_diagram()
    print("✅ Data flow diagram saved as: bedrock_data_flow.png")
    
    # Show the diagrams
    plt.show()
    
    print("\n📊 Architecture diagrams generated successfully!")
    print("Files created:")
    print("  - bedrock_monitoring_architecture.png (Main architecture)")
    print("  - bedrock_monitoring_architecture.pdf (PDF version)")
    print("  - bedrock_data_flow.png (Data flow diagram)")