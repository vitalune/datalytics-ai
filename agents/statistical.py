"""
Statistical Analysis Agent
Uses E2B + Claude to perform quantitative analysis
"""
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic
import json
import os

async def run_statistical_analysis(csv_path: str) -> dict:
    """
    Run comprehensive statistical analysis using E2B sandbox + Claude
    
    Args:
        csv_path: Path to CSV file to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    print("📊 Starting Statistical Analysis Agent...")
    
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
        
        # Create analysis prompt
        prompt = f"""You are a statistical analyst. A dataset has been uploaded to {dataset_path.path}.

Your task: Perform comprehensive statistical analysis including:
1. Summary statistics (mean, median, std dev, min, max, quartiles) for ALL numeric columns
2. Correlation analysis - find correlations with |r| > 0.3 and report them
3. Distribution analysis - test for normality using Shapiro-Wilk test (sample max 5000 rows)
4. Identify the 3 strongest relationships in the data

Write Python code that:
- Loads the CSV with pandas
- Computes all statistics
- Creates a comprehensive results dictionary
- Prints the results as JSON

IMPORTANT: Print the results as a valid JSON object at the end."""

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
            
            print("   ✓ Received analysis code from Claude")
            print(f"\n{'='*60}\nCode to execute:\n{'='*60}\n{code}\n{'='*60}\n")
            
            # Execute in E2B sandbox
            execution = sandbox.run_code(code)
            
            if execution.error:
                print(f"   ✗ Execution error: {execution.error}")
                results = {
                    "error": str(execution.error),
                    "traceback": execution.error.traceback if hasattr(execution.error, 'traceback') else None
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
                    else:
                        results = {
                            "raw_output": stdout_text,
                            "results": [str(r) for r in execution.results]
                        }
                except json.JSONDecodeError:
                    results = {
                        "raw_output": stdout_text,
                        "results": [str(r) for r in execution.results]
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
        sandbox.kill()
        print("   ✓ Sandbox closed")
        print("✅ Statistical Analysis Complete\n")
        
        return results
        
    except Exception as e:
        print(f"❌ Statistical analysis failed: {e}")
        return {"error": str(e)}