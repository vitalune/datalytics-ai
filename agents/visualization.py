"""
Visualization Agent
Uses E2B + Claude to generate data visualizations
"""
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic
import os

async def run_visualization(csv_path: str) -> dict:
    """
    Generate visualizations using E2B sandbox + Claude
    
    Args:
        csv_path: Path to CSV file to visualize
        
    Returns:
        Dictionary containing base64-encoded charts
    """
    print("📈 Starting Visualization Agent...")
    
    try:
        # Create E2B sandbox
        sandbox = Sandbox.create()
        print("   ✓ E2B sandbox created")
        
        # Upload dataset
        with open(csv_path, "rb") as f:
            dataset_path = sandbox.files.write("data.csv", f)
        print(f"   ✓ Dataset uploaded to {dataset_path.path}")
        
        # Initialize Claude
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Create visualization prompt
        prompt = f"""You are a data visualization expert. A dataset has been uploaded to {dataset_path.path}.

Your task: Create 4 insightful visualizations:
1. **Correlation Heatmap** - Show relationships between numeric variables
2. **Revenue Distribution** - Histogram with KDE overlay
3. **Revenue vs Marketing Spend** - Scatter plot with trend line
4. **Revenue Over Time** - Time series with rolling average

Write Python code that:
- Loads the CSV with pandas
- Creates all 4 charts using matplotlib/seaborn
- Uses proper styling (figure size, labels, titles, colors)
- Each chart should be created in a separate cell/figure

IMPORTANT: After creating each plot, the plot will be automatically captured. Just use plt.figure() for each new plot."""

        messages = [{"role": "user", "content": prompt}]
        
        # Define tool for code execution
        tools = [{
            "name": "execute_python",
            "description": "Execute Python code in the E2B sandbox to create visualizations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }]
        
        # Get Claude's response
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            messages=messages,
            tools=tools
        )
        
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute code if Claude calls the tool
        charts = []
        if response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            code = tool_use.input["code"]
            
            print("   ✓ Received visualization code from Claude")
            print(f"\n{'='*60}\nCode to execute:\n{'='*60}\n{code}\n{'='*60}\n")
            
            # Execute in E2B sandbox
            execution = sandbox.run_code(code)
            
            if execution.error:
                print(f"   ✗ Execution error: {execution.error}")
                return {
                    "error": str(execution.error),
                    "charts": []
                }
            else:
                print("   ✓ Code executed successfully")
                
                # E2B automatically captures matplotlib plots as PNG
                chart_count = 0
                for result in execution.results:
                    if hasattr(result, 'png') and result.png:
                        charts.append({
                            "base64": result.png,
                            "type": f"chart_{chart_count}",
                            "format": "png"
                        })
                        chart_count += 1
                        print(f"   ✓ Captured chart {chart_count}")
                
                if chart_count == 0:
                    print("   ⚠ No charts captured, checking saved files...")
                    # Check if files were saved to disk
                    files = sandbox.files.list("/home/user")
                    for file_info in files:
                        if file_info.name.endswith('.png'):
                            print(f"   ✓ Found saved chart: {file_info.name}")
                            import base64
                            content = sandbox.files.read(file_info.path)
                            charts.append({
                                "base64": base64.b64encode(content).decode(),
                                "type": file_info.name,
                                "format": "png"
                            })
                
                print(f"   ✓ Total charts generated: {len(charts)}")
        
        # Clean up
        sandbox.kill()
        print("   ✓ Sandbox closed")
        print("✅ Visualization Complete\n")
        
        return {"charts": charts, "count": len(charts)}
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return {"error": str(e), "charts": []}