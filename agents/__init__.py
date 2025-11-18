"""
Multi-Agent Data Analysis System
"""
from .statistical import run_statistical_analysis
from .visualization import create_visualizations, create_visualization_html
from .anomaly import run_anomaly_detection
from .coordinator import synthesize_insights

__all__ = [
    'run_statistical_analysis',
    'create_visualizations',
    'create_visualization_html',
    'run_anomaly_detection',
    'synthesize_insights'
]