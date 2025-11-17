"""
Coordinator Agent
Synthesizes findings from all agents into business insights
"""
from anthropic import Anthropic
import json
import os

async def synthesize_insights(stats_results: dict, viz_results: dict, anomaly_results: dict) -> str:
    """
    Synthesize findings from all agents into business recommendations
    
    Args:
        stats_results: Results from statistical analysis
        viz_results: Results from visualization
        anomaly_results: Results from anomaly detection
        
    Returns:
        String containing business insights report
    """
    print("🧠 Starting Insights Synthesis Agent...")
    
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Prepare synthesis prompt
        prompt = f"""You are a business strategy consultant. You've received analysis from 3 specialist teams:

**STATISTICAL ANALYSIS TEAM:**
{json.dumps(stats_results, indent=2, default=str)}

**VISUALIZATION TEAM:**
Generated {viz_results.get('count', 0)} charts showing data patterns and relationships.

**ANOMALY DETECTION TEAM:**
{json.dumps(anomaly_results, indent=2, default=str)}

Your task: Create a compelling executive report with:

## Executive Summary
3-4 sentence overview of the most critical findings

## Key Findings
Top 5 insights that matter most for business decisions. For each:
- What the data shows
- Why it matters
- Supporting evidence from the analysis

## Recommendations
3-5 actionable recommendations with:
- Specific action to take
- Expected impact
- Priority level (High/Medium/Low)

## Risk Assessment
2-3 key risks identified from the data quality and anomaly analysis

## Data Quality Notes
Brief summary of data issues found and their potential impact

Use clear, business-friendly language. Be specific with numbers where available. Focus on actionable insights."""

        print("   ✓ Sending synthesis request to Claude...")
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        insights = response.content[0].text
        
        print("   ✓ Insights synthesis complete")
        print("✅ Coordinator Complete\n")
        
        return insights
        
    except Exception as e:
        print(f"❌ Insights synthesis failed: {e}")
        return f"Error generating insights: {str(e)}"