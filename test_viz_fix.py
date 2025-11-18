"""
Test script to verify visualization generation with improved prompt
"""
import asyncio
import os
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

async def test_visualization_generation():
    """Test if improved prompt generates actual visualizations"""
    print("=" * 70)
    print("TEST: Visualization Generation")
    print("=" * 70)

    # Create E2B sandbox
    sandbox = Sandbox.create()
    print("✓ E2B sandbox created")

    # Upload dataset
    csv_path = "test_data/sales_data.csv"
    with open(csv_path, "rb") as f:
        dataset_path = sandbox.files.write("data.csv", f)
    print(f"✓ Dataset uploaded to {dataset_path.path}")

    # Initialize Claude
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Test 1: Original problematic prompt
    print("\n" + "-" * 70)
    print("TEST 1: Original Prompt (expects failure)")
    print("-" * 70)

    old_prompt = f"""You are a data visualization expert. A dataset has been uploaded to {dataset_path.path}.

Your task: Create 4 insightful visualizations:
1. **Correlation Heatmap** - Show relationships between numeric variables
2. **Revenue Distribution** - Histogram with KDE overlay
3. **Revenue vs Marketing Spend** - Scatter plot with trend line
4. **Revenue Over Time** - Time series with rolling average

Write Python code that creates all 4 charts. MUST call plt.show() after each plot."""

    response1 = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": old_prompt}],
        tools=[{
            "name": "execute_python",
            "description": "Execute Python code",
            "input_schema": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"]
            }
        }]
    )

    if response1.stop_reason == "tool_use":
        tool_use = next(block for block in response1.content if block.type == "tool_use")
        code = tool_use.input["code"]

        # Count plt.show() calls in generated code
        show_count = code.count("plt.show()")
        print(f"Generated code contains {show_count} plt.show() calls")
        print(f"Code length: {len(code)} characters")

        # Check if code contains actual plotting
        has_plotting = any(keyword in code for keyword in ["plt.plot", "plt.bar", "plt.scatter", "sns.heatmap", "plt.hist"])
        print(f"Contains plotting commands: {has_plotting}")

        if not has_plotting:
            print("❌ FAILED: Code does not contain visualization commands")
        else:
            print("✓ PASSED: Code contains visualization commands")
    else:
        print(f"❌ FAILED: Claude did not call tool. Stop reason: {response1.stop_reason}")

    # Test 2: Improved adaptive prompt
    print("\n" + "-" * 70)
    print("TEST 2: Improved Adaptive Prompt (expects success)")
    print("-" * 70)

    improved_prompt = f"""You are a data visualization expert. A dataset has been uploaded to {dataset_path.path}.

STEP 1: First, load the data and examine its structure to understand what columns are available.

STEP 2: Based on the available columns, create 4 insightful visualizations. Choose appropriate visualizations such as:
- Correlation heatmap for numeric columns
- Distribution plots for key numeric variables
- Scatter plots showing relationships between variables
- Time series plots if date columns exist
- Category analysis if categorical columns exist

CRITICAL REQUIREMENTS:
1. You MUST create exactly 4 separate visualizations
2. Each visualization MUST be followed by plt.show() to display it
3. Use plt.figure() before each new plot
4. Choose visualizations that match the actual columns in the dataset

Example structure:
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('{dataset_path.path}')

# Chart 1
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.show()  # REQUIRED

# Chart 2
plt.figure(figsize=(10, 6))
# ... create plot based on actual columns ...
plt.show()  # REQUIRED

# Continue for charts 3 and 4...
```

Write the complete Python code now."""

    response2 = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": improved_prompt}],
        tools=[{
            "name": "execute_python",
            "description": "Execute Python code",
            "input_schema": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"]
            }
        }]
    )

    if response2.stop_reason == "tool_use":
        tool_use = next(block for block in response2.content if block.type == "tool_use")
        code = tool_use.input["code"]

        # Count plt.show() calls
        show_count = code.count("plt.show()")
        print(f"Generated code contains {show_count} plt.show() calls")
        print(f"Code length: {len(code)} characters")

        # Check if code contains actual plotting
        has_plotting = any(keyword in code for keyword in ["plt.plot", "plt.bar", "plt.scatter", "sns.heatmap", "plt.hist"])
        print(f"Contains plotting commands: {has_plotting}")

        if has_plotting and show_count >= 4:
            print("✓ PASSED: Code contains visualization commands and multiple plt.show() calls")

            # Actually execute the code to verify it works
            print("\nExecuting code in sandbox...")
            execution = sandbox.run_code(code)

            if execution.error:
                print(f"❌ Execution error: {execution.error}")
            else:
                print(f"✓ Code executed successfully")
                print(f"Number of results: {len(execution.results)}")

                chart_count = 0
                for i, result in enumerate(execution.results):
                    if hasattr(result, 'png') and result.png:
                        chart_count += 1
                        print(f"✓ Chart {chart_count} captured (base64 length: {len(result.png)})")

                if chart_count > 0:
                    print(f"\n✅ SUCCESS: Generated {chart_count} charts!")
                else:
                    print(f"\n❌ FAILED: No charts captured despite having plt.show() calls")
        else:
            print(f"❌ FAILED: Code missing visualizations (has_plotting={has_plotting}, show_count={show_count})")
    else:
        print(f"❌ FAILED: Claude did not call tool. Stop reason: {response2.stop_reason}")

    # Cleanup
    sandbox.kill()
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_visualization_generation())
