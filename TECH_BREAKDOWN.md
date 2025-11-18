# Technical Breakdown: Agent Implementation

A comprehensive technical guide to the multi-agent data analysis system architecture, algorithms, and implementation details.

---

## System Architecture Overview

The system consists of 4 specialized agents orchestrated by a main coordinator:

```
Input CSV
    ↓
    ├─→ [Statistical Agent] ──→
    │   (E2B Sandbox)          Parallel
    │                          Execution
    ├─→ [Anomaly Agent] ──────→
    │   (E2B Sandbox)
    │
    └─→ [Visualization Agent]
        (Local Execution)
            ↓
    [Results]
         ↓
    [Coordinator Agent]
    (Claude Sonnet)
         ↓
    [Insights Generation]
         ↓
    [HTML Report]
```

---

## 1. Statistical Analysis Agent

**File:** `agents/statistical.py`

### Purpose
Performs comprehensive statistical analysis on datasets using Claude-generated code executed in isolated E2B sandboxes.

### Architecture

#### Sandbox Setup
```python
# Create isolated Python environment
sandbox = Sandbox.create()

# Upload CSV to sandbox filesystem
with open(csv_path, "rb") as f:
    dataset_path = sandbox.files.write("data.csv", f)
```

**Key Points:**
- Each execution gets a fresh, isolated sandbox
- No state persistence between runs
- All code execution is sandboxed for security
- File I/O through sandbox.files API

#### Claude Code Generation Flow

1. **Prompt Claude with dataset info:**
   ```python
   messages = [
       {"role": "user", "content": f"Analyze {dataset_path} and compute..."}
   ]
   ```

2. **Claude responds with tool_use:**
   ```python
   response = client.messages.create(
       model="claude-haiku-4-5-20251001",
       tools=[{"name": "code_execute", "description": "..."}],
       messages=messages
   )
   ```

3. **Extract and execute code:**
   ```python
   if response.stop_reason == "tool_use":
       tool_use = next(block for block in response.content
                      if block.type == "tool_use")
       code = tool_use.input["code"]
       execution = sandbox.run_code(code)
   ```

4. **Parse JSON results from stdout:**
   ```python
   stdout_text = "\n".join(execution.logs.stdout)
   json_start = stdout_text.rfind('{')
   json_end = stdout_text.rfind('}') + 1
   results = json.loads(stdout_text[json_start:json_end])
   ```

### Statistical Methods Implemented

Claude generates code to compute:

| Method | Algorithm | Implementation |
|--------|-----------|-----------------|
| **Descriptive Statistics** | Mean, Median, Std Dev, Quartiles | pandas `.describe()` and numpy functions |
| **Correlation Analysis** | Pearson correlation coefficient | `df.corr()` with |r| > 0.3 threshold |
| **Normality Testing** | Shapiro-Wilk test | `scipy.stats.shapiro()` (limited to 5000 rows) |
| **Distribution Analysis** | Skewness, kurtosis detection | Scipy statistical measures |

### Example Generated Code Pattern

Claude typically generates code following this structure:

```python
import pandas as pd
import numpy as np
from scipy import stats

# Load data
df = pd.read_csv('/home/user/data.csv')

# Compute statistics
stats_dict = {
    'mean': df.select_dtypes(include='number').mean().to_dict(),
    'std': df.select_dtypes(include='number').std().to_dict(),
    'correlations': find_correlations(df),
    'normality': test_normality(df),
}

# Output as JSON
print(json.dumps(stats_dict))
```

### Error Handling

```python
# Capture sandbox execution errors
if execution.error:
    results = {
        "error": str(execution.error),
        "traceback": getattr(execution.error, 'traceback', None)
    }
    return results

# Handle JSON parsing failures
try:
    results = json.loads(json_str)
except json.JSONDecodeError:
    results = {
        "raw_output": stdout_text,
        "parsing_error": "Could not extract JSON"
    }
```

### Output Structure

```json
{
  "statistics": {
    "mean": {"column1": 123.45, "column2": 456.78},
    "std": {"column1": 12.34, "column2": 45.67},
    "min": {...},
    "max": {...},
    "quartiles": {...}
  },
  "correlations": [
    {"pair": ["col_a", "col_b"], "coefficient": 0.87}
  ],
  "normality": {
    "shapiro_results": {...}
  },
  "interpretation": "Analysis of the distribution shows..."
}
```

---

## 2. Visualization Agent

**File:** `agents/visualization.py`

### Purpose
Generates 4 standard publication-ready visualizations using matplotlib/seaborn.

### Key Design: Local Execution

Unlike Statistical/Anomaly agents, Visualization runs **locally** (no sandbox):
- Direct filesystem access
- Faster execution (~1-2 seconds)
- Lower overhead
- Direct matplotlib rendering

### Chart Generation Strategy

#### Chart 1: Sales by Category

```python
def create_category_chart():
    try:
        # Primary: Group by categories, sum total
        grouped = df.groupby('categories')['total'].sum().sort_values(ascending=False)

        plt.figure(figsize=(12, 6))
        grouped.plot(kind='bar', color='steelblue', edgecolor='black', linewidth=1.5)
        plt.title('Sales Revenue by Category')
        plt.ylabel('Total Revenue ($)')
        plt.xlabel('Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('chart_1.png', dpi=100, bbox_inches='tight')

    except Exception:
        # Fallback: Histogram of first numeric column
        df.select_dtypes(include='number').iloc[:, 0].hist()
        plt.savefig('chart_1.png', dpi=100, bbox_inches='tight')
```

**Fallback Strategy:**
- If 'categories' or 'total' columns missing
- Uses first numeric column
- Prevents complete failure

#### Chart 2: Revenue Over Time (Time Series)

```python
def create_timeseries_chart():
    try:
        # Convert to datetime
        df['order_date'] = pd.to_datetime(df['order_date'])

        # Group by date, sum daily revenue
        daily_revenue = df.groupby(df['order_date'].dt.date)['total'].sum()

        plt.figure(figsize=(12, 6))
        plt.plot(daily_revenue.index, daily_revenue.values, 'o-', linewidth=2)
        plt.title('Revenue Over Time')
        plt.xlabel('Date')
        plt.ylabel('Daily Revenue ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('chart_2.png', dpi=100, bbox_inches='tight')

    except Exception:
        # Fallback: Line plot of first numeric column (first 100 rows)
        df.select_dtypes(include='number').iloc[:100, 0].plot(kind='line')
        plt.savefig('chart_2.png', dpi=100, bbox_inches='tight')
```

**Time Series Handling:**
- Attempts pd.to_datetime() conversion
- Handles various date formats automatically
- Falls back to sequential line plot if dates invalid

#### Chart 3: Correlation Scatter Plot

```python
def create_scatter_chart():
    try:
        # Scatter quantity vs price with correlation coefficient
        plt.figure(figsize=(10, 8))
        plt.scatter(df['quantity'], df['price'], alpha=0.6, s=50)

        # Calculate and display correlation
        corr = df['quantity'].corr(df['price'])
        plt.text(0.05, 0.95, f'Correlation: {corr:.3f}',
                transform=plt.gca().transAxes, fontsize=12,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.title('Quantity vs Price Relationship')
        plt.xlabel('Quantity (units)')
        plt.ylabel('Price ($)')
        plt.tight_layout()
        plt.savefig('chart_3.png', dpi=100, bbox_inches='tight')

    except Exception:
        # Fallback: Scatter of first two numeric columns
        numeric_cols = df.select_dtypes(include='number').columns[:2]
        df.plot(x=numeric_cols[0], y=numeric_cols[1], kind='scatter')
        plt.savefig('chart_3.png', dpi=100, bbox_inches='tight')
```

**Correlation Visualization:**
- Pearson correlation coefficient calculated
- Displayed as text overlay on chart
- Indicates relationship strength visually

#### Chart 4: Top N Products by Revenue

```python
def create_topn_chart():
    try:
        # Group by product, sum revenue, get top 10
        top_products = df.groupby('product_names')['total'].sum()\
            .sort_values().tail(10)  # .tail() gets top 10

        plt.figure(figsize=(10, 8))
        top_products.plot(kind='barh', color='teal', edgecolor='black')
        plt.title('Top 10 Products by Revenue')
        plt.xlabel('Total Revenue ($)')
        plt.ylabel('Product Name')
        plt.tight_layout()
        plt.savefig('chart_4.png', dpi=100, bbox_inches='tight')

    except Exception:
        # Fallback: Value counts of first categorical column
        df.select_dtypes(include='object').iloc[:, 0]\
            .value_counts().head(10).plot(kind='barh')
        plt.savefig('chart_4.png', dpi=100, bbox_inches='tight')
```

**Top-N Ranking:**
- Uses `.groupby()` for aggregation
- `.sort_values()` for ordering
- `.tail(10)` to get top 10 (after sort in ascending order)

### HTML Dashboard Generation

Creates a responsive visualization dashboard:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="grid">
        <!-- Chart cards -->
    </div>
</body>
</html>
```

### Key Design Patterns

1. **Try-Except Per Chart:** Prevents one failure from stopping all visualizations
2. **Column Auto-Detection:** Uses `.select_dtypes()` for numeric/categorical columns
3. **Graceful Fallbacks:** Always produces a chart, even with missing expected columns
4. **DPI Setting:** 100 DPI balances quality and file size
5. **Relative Paths:** Uses relative paths for portability across systems

---

## 3. Anomaly Detection Agent

**File:** `agents/anomaly.py`

### Purpose
Detects data quality issues, outliers, and suspicious patterns using statistical methods.

### Architecture

Nearly identical to Statistical Agent:
- E2B Sandbox execution
- Claude code generation
- JSON result parsing
- Tool use mechanism

### Anomaly Detection Methods

Claude generates code to detect:

#### 1. Statistical Outliers (Z-Score Method)

```python
from scipy import stats

# Calculate z-scores for all numeric columns
z_scores = np.abs(stats.zscore(df.select_dtypes(include='number')))

# Find values with |z| > 3 (>99.7th percentile)
outliers = (z_scores > 3).any(axis=1)
```

**Principle:** Values >3 standard deviations from mean are statistical outliers (probability < 0.3%)

#### 2. Impossible Values Detection

```python
# Negative revenue check
impossible_values = {
    'negative_revenue': (df['total'] < 0).sum(),
    'negative_customer_id': (df['customer_id'] < 0).sum(),
    'invalid_quantity': (df['quantity'] < 0).sum(),
    'out_of_range_dates': (df['order_date'] > today()).sum()
}
```

**Logic:** Domain-specific validation (revenue/quantity should never be negative)

#### 3. Missing Values Analysis

```python
# Completeness check
missing_values = {
    col: df[col].isnull().sum()
    for col in df.columns
}

null_percentage = {
    col: (df[col].isnull().sum() / len(df)) * 100
    for col in df.columns
    if df[col].isnull().sum() > 0
}
```

**Purpose:** Identifies data completeness and missing value patterns

#### 4. Duplicate Detection

```python
# Exact row duplicates
duplicate_rows = df.duplicated().sum()

# Partial duplicates (same customer, same product, different date)
partial_dupes = df.duplicated(subset=['customer_id', 'product_id'], keep=False).sum()
```

**Types:** Exact duplicates vs. functional duplicates in business logic

#### 5. Suspicious Patterns

```python
# Repeated exact values (indicator of data entry errors)
for col in df.select_dtypes(include='number').columns:
    value_counts = df[col].value_counts()
    # If single value appears >50% of time, flagged as suspicious
    suspicious = value_counts[value_counts > len(df) * 0.5]
```

**Pattern Recognition:** Detects unnatural data distributions that suggest errors

### Output Structure

```json
{
  "outliers": [
    {
      "row": 42,
      "column": "price",
      "value": 999.99,
      "reason": "z_score",
      "z_score": 4.2
    }
  ],
  "data_quality": {
    "missing_values": {
      "phone": 15,
      "email": 8
    },
    "duplicate_rows": 3,
    "suspicious_patterns": [
      "Column 'status' has 89% of values as 'ACTIVE'"
    ]
  },
  "total_issues": 26,
  "severity": "medium",
  "interpretation": "Data contains 26 quality issues..."
}
```

---

## 4. Coordinator Agent

**File:** `agents/coordinator.py`

### Purpose
Synthesizes findings from all agents into business-focused executive report.

### Key Differences from Other Agents

1. **No E2B Sandbox:** Direct Claude API call (no code generation needed)
2. **More Capable Model:** Uses `claude-sonnet-4-5-20250929` vs haiku
3. **Complex Reasoning:** Requires better model for synthesis
4. **Markdown Output:** Structured text format for parsing

### Synthesis Flow

```python
async def synthesize_insights(
    stats_results: dict,    # From Statistical Agent
    viz_results: dict,      # From Visualization Agent
    anomaly_results: dict   # From Anomaly Agent
) -> str:
```

### Prompt Structure

```python
prompt = f"""
Analyze the following data analysis results and provide a comprehensive business report.

DATA ANALYSIS RESULTS:
{json.dumps(stats_results, indent=2)}

DATA QUALITY:
{json.dumps(anomaly_results, indent=2)}

VISUALIZATIONS: {viz_results.get('count', 4)} charts generated

Please provide:

## Executive Summary
(2-3 sentences of critical findings)

## Key Findings
(5 business-relevant insights with structure:)
1. **Finding Title**
   - What the data shows
   - Why it matters
   - Supporting evidence

## Recommendations
(3-5 actionable recommendations with:)
1. Action description
2. Expected impact
3. Priority (HIGH/MEDIUM/LOW)

## Risk Assessment
(2-3 key risks identified)

## Data Quality Notes
(Summary of anomalies found)
"""
```

### Markdown-to-HTML Parsing

The returned markdown is parsed in `main.py`:

```python
def parse_insights(insights: str) -> dict:
    """Convert markdown sections into dict"""
    sections = {}
    current_section = None

    for line in insights.split('\n'):
        if line.startswith('## '):
            # Extract section name
            current_section = line.replace('## ', '').strip()
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())

    return sections

def build_insights_html(sections: dict) -> str:
    """Convert sections to interactive HTML"""
    html = ""

    for section_name, content in sections.items():
        section_id = section_name.lower().replace(' ', '-')

        # Create collapsible button
        html += f"""
        <button class="collapsible" data-section="{section_id}"
                onclick="toggleSection(this);">
            {section_name}
            <span class="collapse-icon">▶</span>
        </button>
        <div class="content" id="content-{section_id}">
        """

        # Parse content lines into formatted HTML
        for line in content:
            if line.startswith('### '):
                html += f'<h4>{line.replace("### ", "")}</h4>'
            elif '**' in line and ':' in line:
                # Extract title and description
                parts = line.split(':', 1)
                title = parts[0].replace('**', '').strip()
                desc = parts[1].strip() if len(parts) > 1 else ''
                html += f'<div class="finding-card"><h4>{title}</h4><p>{desc}</p></div>'
            else:
                html += f'<p>{line}</p>'

        html += '</div>'

    return html
```

---

## Data Flow & Execution Model

### Parallel Execution Strategy

```python
# Main orchestrator uses asyncio for parallelism
async def main():
    # Run Statistical + Anomaly in parallel (both use E2B)
    stats_results, anomaly_results = await asyncio.gather(
        run_statistical_analysis(csv_path),      # ~10-20 seconds
        run_anomaly_detection(csv_path)          # ~10-20 seconds
    )
    # Total time: ~20 seconds (not 40)

    # Visualization runs locally (fast, no need to parallelize)
    viz_results = create_visualizations(csv_path)  # ~1-2 seconds

    # Synthesis uses results from all agents
    insights = await synthesize_insights(
        stats_results, viz_results, anomaly_results
    )  # ~3-5 seconds

    # Report generation (fast)
    html_report = generate_html_report(insights, charts, stats, anomalies)
```

### Complete Execution Timeline

```
T=0s     ├─ Start Statistical Agent (E2B) ────────────┐
         ├─ Start Anomaly Agent (E2B) ───────────────┤
         │                                            │
T=15s    │                                            │
         │                                            ├─ Both Complete
         │                                            │
T=20s    ├─ Start Visualization Agent (Local) ───────┤
         │                         ~2 seconds         │
T=22s    ├─ Visualization Complete ─────────────────┘
         │
         ├─ Start Coordinator Synthesis ──────────────┐
         │                    ~4 seconds              │
T=26s    ├─ Insights Complete ────────────────────────┤
         │                                            │
         ├─ Generate HTML Report ──────────────────┐  │
         │                    <1 second             │  │
T=26.5s  └─ Report Complete ──────────────────────┘──┘

Total: ~26 seconds (vs ~45 if sequential)
Speedup: ~1.7x from parallelization
```

---

## Technical Algorithms Deep Dive

### Statistical Algorithms

#### Pearson Correlation Coefficient
```
r = Σ[(x_i - mean_x)(y_i - mean_y)] / √[Σ(x_i - mean_x)² × Σ(y_i - mean_y)²]

Range: -1 to 1
Interpretation:
  ≈ 1: Perfect positive correlation
  ≈ 0: No correlation
  ≈ -1: Perfect negative correlation
```

Threshold for reporting: |r| > 0.3 (moderate correlation)

#### Shapiro-Wilk Normality Test
```
Test statistic: W = (Σ a_i × x_(i))² / Σ(x_i - x̄)²

H₀: Data is normally distributed
p-value < 0.05: Reject H₀ (data is NOT normal)

Limitations: Only for n ≤ 5000 (CPU intensive)
```

#### Z-Score Outlier Detection
```
z = (x - μ) / σ

|z| > 3: Extremely rare (p < 0.003)
|z| > 2: Unusual (p < 0.05)
|z| > 1: Uncommon (p < 0.16)
```

Threshold: |z| > 3 ensures <0.3% false positive rate

### Visualization Algorithms

#### Groupby Aggregation Pattern
```python
# Pattern: group + aggregate + sort + limit
df.groupby('category')['revenue'].sum() \
  .sort_values(ascending=False) \
  .head(10)

# Computational complexity: O(n) groupby + O(k log k) sort
# where k = number of groups
```

#### Date Parsing and Bucketing
```python
# Convert string to datetime
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)

# Bucket by day/month/year
daily = df.groupby(df['date'].dt.date)['value'].sum()

# Complexity: O(n) for parsing, O(n) for bucketing
```

---

## Error Handling Architecture

### Multi-Level Error Catching

```python
# Level 1: Sandbox execution errors
try:
    execution = sandbox.run_code(code)
    if execution.error:
        return {"error": str(execution.error)}
except Exception as e:
    return {"error": f"Sandbox error: {str(e)}"}

# Level 2: JSON parsing errors
try:
    results = json.loads(json_str)
except json.JSONDecodeError:
    return {"raw_output": stdout_text}

# Level 3: Chart generation (try-except per chart)
for i, config in enumerate(chart_configs):
    try:
        create_chart(config)
    except Exception:
        # Try fallback, don't stop processing
        create_fallback_chart(config)
```

### Graceful Degradation

- Agent fails → Return available partial results
- Chart fails → Try fallback chart type
- Parsing fails → Return raw output
- Report generation fails → Return plain text report

---

## Performance Optimization Techniques

### 1. Lazy Evaluation
```python
# Don't load entire dataset if not needed
df.head(100)  # Preview before full analysis
df.sample(1000)  # Random sample for large datasets
```

### 2. Data Type Optimization
```python
# Use appropriate dtypes to reduce memory
df['category'] = df['category'].astype('category')
df['date'] = pd.to_datetime(df['date'])
```

### 3. Vectorization
```python
# Vectorized operations (fast)
df['new_col'] = df['col1'] + df['col2']

# vs. Loop (slow)
for i, row in df.iterrows():
    df.at[i, 'new_col'] = row['col1'] + row['col2']
```

### 4. Model Selection
- **Haiku:** Faster, cheaper (used for agents)
- **Sonnet:** Better reasoning (used for synthesis)
- Trade-off optimized for this use case

### 5. Async Parallelization
```python
# Spawn 2 E2B sandboxes in parallel
results = await asyncio.gather(
    agent1(),  # Runs concurrently
    agent2()   # Runs concurrently
)
# vs Sequential: await agent1() + await agent2()
```

---

## Key Design Decisions

### 1. Why E2B for Some Agents?
- **Statistical & Anomaly:** Complex computations benefit from isolation
- **Visualization:** Simple Python calls, runs locally for speed
- **Security:** Untrusted user code runs in sandbox

### 2. Why Claude for Code Generation?
- Flexible to any column names or data structure
- Handles edge cases automatically
- Can reason about data semantics
- Better than hardcoded pandas pipelines

### 3. Why Markdown for Insights?
- Human readable
- Easy to parse back to HTML
- Structured sections (##) enable collapsing
- AI naturally generates markdown

### 4. Why Glassmorphism Design?
- Modern aesthetic appeals to users
- Blur effects hide complex backgrounds
- Smooth animations reduce perceived latency
- Dark mode reduces eye strain

---

## Extensibility & Future Improvements

### Easy Extensions

1. **Add New Agents:**
   ```python
   # Follow template
   async def run_ml_agent(csv_path):
       sandbox = Sandbox.create()
       # ... upload data ...
       # ... generate code ...
       # ... execute ...
       return results

   # Add to orchestrator
   ml_results = await run_ml_agent(csv_path)
   ```

2. **Add New Charts:**
   ```python
   def create_pie_chart():
       df.groupby('category')['revenue'].sum().plot(kind='pie')
       plt.savefig('chart_pie.png', dpi=100)
   ```

3. **Add New Statistics:**
   Update Claude prompt to include new methods

### Harder Extensions

1. **Real-time Streaming:** Requires architecture redesign
2. **Distributed Execution:** Need multiple E2B orgs
3. **Custom Models:** Requires fine-tuning infrastructure
4. **Database Integration:** Add SQL generation agent

---

## Testing Strategy

### Unit Testing Approach

```python
def test_statistical_agent():
    # Create small test dataset
    test_csv = "test_data_small.csv"

    # Run agent
    results = run_statistical_analysis(test_csv)

    # Verify structure
    assert 'statistics' in results
    assert 'interpretation' in results

    # Verify values
    assert results['statistics']['mean'] > 0
```

### Integration Testing

```python
def test_full_pipeline():
    # Run complete pipeline
    results = await main()

    # Verify all outputs exist
    assert os.path.exists('results/analysis_report.html')
    assert os.path.exists('results/chart_1.png')
    assert len(results['insights']) > 0
```

---

## Monitoring & Debugging

### Logging Strategy
```python
print(f"   ✓ Statistical analysis complete ({duration}s)")
print(f"   ✓ Generated {len(charts)} visualizations")
print(f"   ✓ Detected {anomalies['total_issues']} data quality issues")
```

### Error Visibility
```python
if execution.error:
    print(f"   ✗ Error in agent: {execution.error}")
    print(f"   Stderr: {execution.logs.stderr}")
```

### Performance Tracking
```python
import time
start = time.time()
results = await run_statistical_analysis(csv_path)
duration = time.time() - start
print(f"⏱️  Statistical Analysis: {duration:.1f}s")
```

---

## Summary Table

| Component | Technology | Purpose | Time |
|-----------|-----------|---------|------|
| **Statistical Agent** | Claude + E2B | Statistics & correlations | 10-20s |
| **Visualization Agent** | Matplotlib/Seaborn | Chart generation | 1-2s |
| **Anomaly Agent** | Claude + E2B | Quality detection | 10-20s |
| **Coordinator Agent** | Claude Sonnet | Insight synthesis | 3-5s |
| **HTML Report** | HTML/CSS/JS | Interactive display | <1s |
| **Total Execution** | Async orchestration | Complete pipeline | ~25-30s |

---

## References & Resources

- [Claude API Documentation](https://docs.anthropic.com)
- [E2B Sandbox Documentation](https://e2b.dev)
- [Pandas Documentation](https://pandas.pydata.org)
- [Matplotlib Documentation](https://matplotlib.org)
- [SciPy Statistics](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Shapiro-Wilk Test](https://en.wikipedia.org/wiki/Shapiro%E2%80%93Wilk_test)
- [Z-Score Method](https://en.wikipedia.org/wiki/Standard_score)
