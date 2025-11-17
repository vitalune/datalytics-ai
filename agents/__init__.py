"""
Multi-Agent Data Analysis System
"""
from .statistical import run_statistical_analysis
from .visualization import run_visualization
from .anomaly import run_anomaly_detection
from .coordinator import synthesize_insights

__all__ = [
    'run_statistical_analysis',
    'run_visualization',
    'run_anomaly_detection',
    'synthesize_insights'
]