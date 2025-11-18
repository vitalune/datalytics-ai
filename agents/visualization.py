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

Your task is to create EXACTLY 4 insightful visualizations based on the actual columns in the dataset.

STEP 1: Load the data and examine what columns are available.

STEP 2: Create 4 visualizations adapted to the data. Choose from:
- **Correlation heatmap** if multiple numeric columns exist
- **Distribution plots** (histogram with KDE) for key numeric variables
- **Scatter plots** showing relationships between numeric variables
- **Time series plots** if date columns exist
- **Category analysis** (bar charts) if categorical columns exist
- **Box plots** for comparing distributions across categories

CRITICAL REQUIREMENTS:
1. You MUST create EXACTLY 4 separate visualizations
2. Each visualization MUST end with plt.show() - this is how charts are captured
3. Use plt.figure(figsize=(10, 6)) before each new plot
4. Choose visualizations based on the ACTUAL columns in the dataset, not assumptions
5. Make charts visually appealing with titles, labels, and colors

REQUIRED CODE STRUCTURE:
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('{dataset_path.path}')

# Chart 1
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.title('Chart 1 Title')
plt.show()  # MUST HAVE THIS

# Chart 2
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.title('Chart 2 Title')
plt.show()  # MUST HAVE THIS

# Chart 3
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.title('Chart 3 Title')
plt.show()  # MUST HAVE THIS

# Chart 4
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.title('Chart 4 Title')
plt.show()  # MUST HAVE THIS
```

Write the complete code now. Remember: 4 charts, each with plt.show()."""

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

            # Validate the generated code contains visualizations
            show_count = code.count("plt.show()")
            has_plotting = any(keyword in code for keyword in [
                "plt.plot", "plt.bar", "plt.scatter", "plt.hist",
                "sns.heatmap", "sns.scatterplot", "sns.barplot", "sns.boxplot"
            ])

            print("   ✓ Received visualization code from Claude")
            print(f"   ℹ Code validation: plt.show() count={show_count}, has_plotting={has_plotting}")

            # If code doesn't have visualizations, retry with stronger prompt
            if not has_plotting or show_count < 4:
                print("   ⚠ Generated code lacks proper visualizations, retrying with explicit instructions...")

                retry_prompt = f"""Your previous code did not create visualizations. You MUST create 4 matplotlib/seaborn charts.

DO NOT just explore the data. CREATE 4 ACTUAL PLOTS.

Here's what you MUST do:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('{dataset_path.path}')

# Chart 1: Correlation Heatmap
plt.figure(figsize=(10, 6))
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Heatmap')
plt.show()

# Chart 2: Distribution of first numeric column
plt.figure(figsize=(10, 6))
numeric_col = df.select_dtypes(include=['int64', 'float64']).columns[0]
plt.hist(df[numeric_col], bins=30, edgecolor='black', alpha=0.7)
plt.title(f'Distribution of {{numeric_col}}')
plt.xlabel(numeric_col)
plt.ylabel('Frequency')
plt.show()

# Chart 3: Scatter plot of two numeric columns
plt.figure(figsize=(10, 6))
num_cols = df.select_dtypes(include=['int64', 'float64']).columns
plt.scatter(df[num_cols[0]], df[num_cols[1]], alpha=0.5)
plt.title(f'{{num_cols[0]}} vs {{num_cols[1]}}')
plt.xlabel(num_cols[0])
plt.ylabel(num_cols[1])
plt.show()

# Chart 4: Category counts if categorical columns exist, else another distribution
plt.figure(figsize=(10, 6))
cat_cols = df.select_dtypes(include=['object']).columns
if len(cat_cols) > 0:
    df[cat_cols[0]].value_counts().head(10).plot(kind='bar')
    plt.title(f'Top 10 {{cat_cols[0]}} Values')
    plt.xlabel(cat_cols[0])
    plt.ylabel('Count')
else:
    num_col = df.select_dtypes(include=['int64', 'float64']).columns[1]
    plt.hist(df[num_col], bins=30, edgecolor='black', alpha=0.7)
    plt.title(f'Distribution of {{num_col}}')
    plt.xlabel(num_col)
    plt.ylabel('Frequency')
plt.tight_layout()
plt.show()
```

Create code similar to above that works with the actual dataset. MUST have 4 plt.show() calls."""

                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": "Please provide code that creates 4 visualizations with plt.show() calls."
                    }]
                })

                messages.append({"role": "user", "content": retry_prompt})

                retry_response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4000,
                    messages=messages,
                    tools=tools
                )

                if retry_response.stop_reason == "tool_use":
                    tool_use = next(block for block in retry_response.content if block.type == "tool_use")
                    code = tool_use.input["code"]
                    show_count = code.count("plt.show()")
                    print(f"   ✓ Retry generated code with {show_count} plt.show() calls")

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
                print(f"   ℹ Number of execution results: {len(execution.results)}")

                # E2B automatically captures matplotlib plots as PNG
                chart_count = 0
                for i, result in enumerate(execution.results):
                    print(f"   ℹ Result {i}: type={type(result)}, has png={hasattr(result, 'png')}")

                    if hasattr(result, 'png') and result.png:
                        charts.append({
                            "base64": result.png,
                            "type": f"chart_{chart_count}",
                            "format": "png"
                        })
                        chart_count += 1
                        print(f"   ✓ Captured chart {chart_count}")
                    elif hasattr(result, 'formats'):
                        print(f"   ℹ Available formats: {result.formats()}")

                if chart_count == 0:
                    print("   ⚠ No charts captured from execution results")
                    print("   ℹ Stdout output:")
                    if execution.logs and execution.logs.stdout:
                        for line in execution.logs.stdout[:10]:  # First 10 lines
                            print(f"     {line}")

                    print("   ℹ Checking for saved PNG files...")
                    # Check if files were saved to disk
                    try:
                        files = sandbox.files.list("/home/user")
                        print(f"   ℹ Found {len(files)} files in /home/user")
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
                                chart_count += 1
                    except Exception as e:
                        print(f"   ✗ Error checking files: {e}")

                print(f"   ✓ Total charts generated: {len(charts)}")
        
        # Clean up
        sandbox.kill()
        print("   ✓ Sandbox closed")
        print("✅ Visualization Complete\n")
        
        return {"charts": charts, "count": len(charts)}
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return {"error": str(e), "charts": []}