"""
Anomaly Detection Agent
Uses E2B + Claude to detect outliers and data quality issues
"""
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic
import json
import os

async def run_anomaly_detection(csv_path: str) -> dict:
    """
    Detect anomalies and data quality issues using E2B sandbox + Claude
    
    Args:
        csv_path: Path to CSV file to analyze
        
    Returns:
        Dictionary containing detected anomalies
    """
    print("🔍 Starting Anomaly Detection Agent...")
    
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
        
        # Create anomaly detection prompt
        prompt = f"""You are an anomaly detection specialist. A dataset has been uploaded to {dataset_path.path}.

Your task: Detect ALL data quality issues and anomalies:

1. **Statistical Outliers**: Use Z-score method (|z| > 3) for ALL numeric columns
2. **Impossible Values**: 
   - Negative values where they shouldn't exist (customers, revenue, etc)
   - Values outside valid ranges (e.g., churn_rate > 1)
3. **Missing Values**: Count missing values per column
4. **Duplicate Rows**: Find exact duplicate rows
5. **Suspicious Patterns**: Detect repeated exact values that seem unnatural

Write Python code that:
- Loads the CSV with pandas
- Checks all the above issues
- Creates a comprehensive results dictionary with:
  {{
    "outliers": [list of dicts with row, column, value, reason, z_score],
    "data_quality": {{
      "missing_values": {{column: count}},
      "duplicate_rows": count,
      "suspicious_patterns": [descriptions]
    }},
    "total_issues": count,
    "severity": "low/medium/high"
  }}
- Prints the results as JSON

IMPORTANT: Print the complete results as valid JSON."""

        messages = [{"role": "user", "content": prompt}]
        
        # Define tool for code execution
        tools = [{
            "name": "execute_python",
            "description": "Execute Python code in the E2B sandbox",
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
        results = {}
        if response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            code = tool_use.input["code"]
            
            print("   ✓ Received anomaly detection code from Claude")
            print(f"\n{'='*60}\nCode to execute:\n{'='*60}\n{code}\n{'='*60}\n")
            
            # Execute in E2B sandbox
            execution = sandbox.run_code(code)
            
            if execution.error:
                print(f"   ✗ Execution error: {execution.error}")
                results = {
                    "error": str(execution.error),
                    "outliers": [],
                    "data_quality": {}
                }
            else:
                print("   ✓ Code executed successfully")
                
                # Extract results from stdout
                stdout_text = "\n".join(execution.logs.stdout)
                
                # Try to parse JSON from output
                try:
                    # Find JSON in output
                    json_start = stdout_text.rfind('{')
                    json_end = stdout_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = stdout_text[json_start:json_end]
                        results = json.loads(json_str)
                        print(f"   ✓ Detected {results.get('total_issues', 0)} issues")
                    else:
                        results = {
                            "raw_output": stdout_text,
                            "outliers": [],
                            "data_quality": {}
                        }
                except json.JSONDecodeError:
                    results = {
                        "raw_output": stdout_text,
                        "outliers": [],
                        "data_quality": {}
                    }
                
                # Get Claude's interpretation
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": stdout_text
                    }]
                })
                
                # Ask Claude to summarize
                final_response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    messages=messages,
                    tools=tools
                )
                
                if final_response.content:
                    results["interpretation"] = final_response.content[0].text
                    print("   ✓ Claude's interpretation added")
        
        # Clean up
        sandbox.kill()()
        print("   ✓ Sandbox closed")
        print("✅ Anomaly Detection Complete\n")
        
        return results
        
    except Exception as e:
        print(f"❌ Anomaly detection failed: {e}")
        return {"error": str(e), "outliers": [], "data_quality": {}}