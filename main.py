"""
Main Orchestrator
Coordinates parallel execution of all agents and generates final report
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.statistical import run_statistical_analysis
from agents.visualization import run_visualization
from agents.anomaly import run_anomaly_detection
from agents.coordinator import synthesize_insights

def generate_html_report(insights: str, charts: list, stats: dict, anomalies: dict) -> str:
    """Generate comprehensive HTML report"""
    
    # Format charts HTML
    charts_html = ""
    for i, chart in enumerate(charts):
        charts_html += f"""
        <div class="chart-container">
            <h3>Visualization {i + 1}</h3>
            <img src="data:image/png;base64,{chart['base64']}" alt="Chart {i + 1}">
        </div>
        """
    
    # Format statistics summary
    stats_html = "<h3>Statistical Overview</h3><ul>"
    if "interpretation" in stats:
        stats_html += f"<li><strong>Analysis:</strong> {stats['interpretation'][:500]}...</li>"
    if "raw_output" in stats:
        stats_html += f"<li><pre>{stats['raw_output'][:1000]}</pre></li>"
    stats_html += "</ul>"
    
    # Format anomalies summary
    anomalies_html = "<h3>Data Quality Issues</h3><ul>"
    if "total_issues" in anomalies:
        anomalies_html += f"<li><strong>Total Issues Found:</strong> {anomalies['total_issues']}</li>"
    if "interpretation" in anomalies:
        anomalies_html += f"<li><strong>Summary:</strong> {anomalies['interpretation'][:500]}...</li>"
    anomalies_html += "</ul>"
    
    # Convert markdown-style insights to HTML
    insights_html = insights.replace('\n\n', '</p><p>').replace('\n', '<br>')
    insights_html = insights_html.replace('## ', '<h2>').replace('\n', '</h2>\n')
    insights_html = f"<p>{insights_html}</p>"
    
    # Create full HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Data Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .section h3 {{
            color: #555;
            margin: 20px 0 15px 0;
            font-size: 1.3em;
        }}
        
        .insights {{
            font-size: 1.05em;
            line-height: 1.8;
        }}
        
        .insights p {{
            margin-bottom: 15px;
        }}
        
        .insights ul {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        .insights li {{
            margin-bottom: 10px;
        }}
        
        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        
        .chart-container h3 {{
            color: #764ba2;
            margin-bottom: 15px;
        }}
        
        .chart-container img {{
            width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card h4 {{
            color: #667eea;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #764ba2;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.9em;
            border-left: 4px solid #667eea;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 8px;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Multi-Agent Data Analysis Report</h1>
            <div class="meta">
                <p>Generated by Parallel Analysis Pipeline</p>
                <p>Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><span class="badge badge-success">3 Agents</span> <span class="badge badge-success">{len(charts)} Visualizations</span></p>
            </div>
        </div>
        
        <div class="section insights">
            <h2>📊 Executive Insights</h2>
            {insights_html}
        </div>
        
        <div class="section">
            <h2>📈 Data Visualizations</h2>
            <div class="charts">
                {charts_html}
            </div>
        </div>
        
        <div class="section">
            <h2>📉 Detailed Analysis</h2>
            {stats_html}
        </div>
        
        <div class="section">
            <h2>🔍 Data Quality Assessment</h2>
            {anomalies_html}
        </div>
        
        <div class="footer">
            <p>Powered by E2B Sandboxes + Claude AI</p>
            <p>This report was generated using parallel agent execution in isolated environments</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html

async def main():
    """Main orchestrator function"""
    
    print("\n" + "="*70)
    print("🚀 PARALLEL DATA ANALYSIS PIPELINE")
    print("="*70 + "\n")
    
    # Configuration
    csv_path = "test_data/sales_data.csv"
    
    # Verify file exists
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found!")
        print("   Run 'python generate_sample_data.py' first to create test data.")
        return
    
    print(f"📁 Dataset: {csv_path}")
    print(f"🤖 Agents: 3 (Statistical, Visualization, Anomaly)")
    print(f"⚡ Mode: Parallel Execution\n")
    print("="*70 + "\n")
    
    # Phase 1: Run all analysis agents in parallel
    print("Phase 1: Running Analysis Agents in Parallel...")
    print("-" * 70 + "\n")
    
    start_time = datetime.now()
    
    # Execute all agents concurrently
    stats_results, viz_results, anomaly_results = await asyncio.gather(
        run_statistical_analysis(csv_path),
        run_visualization(csv_path),
        run_anomaly_detection(csv_path)
    )
    
    analysis_time = (datetime.now() - start_time).total_seconds()
    
    print("="*70)
    print(f"✅ ALL ANALYSIS AGENTS COMPLETE ({analysis_time:.1f}s)")
    print("="*70 + "\n")
    
    # Phase 2: Synthesize insights
    print("Phase 2: Synthesizing Insights...")
    print("-" * 70 + "\n")
    
    insights = await synthesize_insights(stats_results, viz_results, anomaly_results)
    
    print("="*70)
    print("✅ INSIGHTS SYNTHESIS COMPLETE")
    print("="*70 + "\n")
    
    # Phase 3: Generate HTML report
    print("Phase 3: Generating Final Report...")
    print("-" * 70 + "\n")
    
    os.makedirs("results", exist_ok=True)
    
    charts = viz_results.get("charts", [])
    html_report = generate_html_report(insights, charts, stats_results, anomaly_results)
    
    report_path = "results/analysis_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    
    print(f"   ✓ HTML report saved to {report_path}")
    
    # Save raw results as JSON for debugging
    import json
    results_json = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats_results,
        "visualizations": {"count": len(charts)},
        "anomalies": anomaly_results,
        "insights": insights
    }
    
    json_path = "results/raw_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2, default=str)
    
    print(f"   ✓ Raw results saved to {json_path}")
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("🎉 ANALYSIS COMPLETE!")
    print("="*70)
    print(f"\n⏱️  Total time: {total_time:.1f}s")
    print(f"📊 Charts generated: {len(charts)}")
    print(f"📁 Results saved in: results/")
    print(f"\n👉 Open {report_path} in your browser to view the full report\n")

if __name__ == "__main__":
    asyncio.run(main())