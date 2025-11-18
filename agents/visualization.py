"""
Visualization Agent
Creates data visualizations using pandas + matplotlib locally
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def create_visualizations(csv_path: str, output_dir: str = "results") -> dict:
    """
    Create 4 standard visualizations from CSV data using matplotlib.

    Args:
        csv_path: Path to CSV file to visualize
        output_dir: Directory to save PNG files

    Returns:
        Dictionary with 'charts' list of file paths and 'count' of charts created
    """
    print("📈 Creating Visualizations with Matplotlib...")

    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load the CSV
        df = pd.read_csv(csv_path)
        print(f"   ✓ Loaded CSV: {df.shape[0]} rows, {df.shape[1]} columns")

        charts = []

        # Chart 1: Sales by Category (Bar Chart)
        print("   ℹ Creating chart 1: Sales by Category")
        try:
            plt.figure(figsize=(12, 6))
            if 'categories' in df.columns and 'total' in df.columns:
                category_sales = df.groupby('categories')['total'].sum().sort_values(ascending=False)
                category_sales.plot(kind='bar', color='steelblue', edgecolor='black', alpha=0.7)
                plt.title('Total Revenue by Category', fontsize=14, fontweight='bold')
                plt.xlabel('Category', fontsize=12)
                plt.ylabel('Revenue ($)', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
            else:
                # Fallback: create a simple distribution if categories don't exist
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    plt.hist(df[numeric_cols[0]], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                    plt.title('Distribution of First Numeric Column', fontsize=14, fontweight='bold')
                    plt.xlabel(numeric_cols[0], fontsize=12)
                    plt.ylabel('Frequency', fontsize=12)

            chart_path = os.path.join(output_dir, 'chart_1.png')
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
            print(f"   ✓ Saved chart 1: {chart_path}")
        except Exception as e:
            print(f"   ⚠ Error creating chart 1: {e}")

        # Chart 2: Revenue Over Time (Line Chart)
        print("   ℹ Creating chart 2: Revenue Over Time")
        try:
            plt.figure(figsize=(12, 6))
            if 'order_date' in df.columns and 'total' in df.columns:
                # Convert to datetime and aggregate
                df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
                daily_revenue = df.groupby(df['order_date'].dt.date)['total'].sum().reset_index()
                daily_revenue.columns = ['Date', 'Revenue']

                plt.plot(daily_revenue['Date'], daily_revenue['Revenue'],
                        marker='o', linewidth=2, markersize=4, color='darkgreen', alpha=0.7)
                plt.title('Daily Revenue Trend', fontsize=14, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Revenue ($)', fontsize=12)
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
            else:
                # Fallback: create a line plot of any numeric column
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    plt.plot(df[numeric_cols[0]].head(100), linewidth=2, color='darkgreen', alpha=0.7)
                    plt.title('Trend Line (First 100 rows)', fontsize=14, fontweight='bold')
                    plt.xlabel('Index', fontsize=12)
                    plt.ylabel(numeric_cols[0], fontsize=12)

            plt.tight_layout()
            chart_path = os.path.join(output_dir, 'chart_2.png')
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
            print(f"   ✓ Saved chart 2: {chart_path}")
        except Exception as e:
            print(f"   ⚠ Error creating chart 2: {e}")

        # Chart 3: Quantity vs Price Scatter Plot
        print("   ℹ Creating chart 3: Quantity vs Price Relationship")
        try:
            plt.figure(figsize=(10, 7))
            if 'quantity' in df.columns and 'price' in df.columns:
                plt.scatter(df['quantity'], df['price'], alpha=0.5, s=50, color='purple', edgecolors='black')
                plt.title('Quantity vs Price Relationship', fontsize=14, fontweight='bold')
                plt.xlabel('Quantity', fontsize=12)
                plt.ylabel('Price ($)', fontsize=12)
                plt.grid(True, alpha=0.3)

                # Add correlation coefficient
                corr = df['quantity'].corr(df['price'])
                plt.text(0.05, 0.95, f'Correlation: {corr:.3f}',
                        transform=plt.gca().transAxes, fontsize=11,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            else:
                # Fallback: scatter plot of any two numeric columns
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) >= 2:
                    plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]],
                              alpha=0.5, s=50, color='purple', edgecolors='black')
                    plt.title(f'{numeric_cols[0]} vs {numeric_cols[1]}', fontsize=14, fontweight='bold')
                    plt.xlabel(numeric_cols[0], fontsize=12)
                    plt.ylabel(numeric_cols[1], fontsize=12)

            plt.tight_layout()
            chart_path = os.path.join(output_dir, 'chart_3.png')
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
            print(f"   ✓ Saved chart 3: {chart_path}")
        except Exception as e:
            print(f"   ⚠ Error creating chart 3: {e}")

        # Chart 4: Top 10 Products by Revenue (Horizontal Bar Chart)
        print("   ℹ Creating chart 4: Top 10 Products by Revenue")
        try:
            plt.figure(figsize=(12, 6))
            if 'product_names' in df.columns and 'total' in df.columns:
                product_revenue = df.groupby('product_names')['total'].sum().sort_values(ascending=True).tail(10)
                product_revenue.plot(kind='barh', color='coral', edgecolor='black', alpha=0.7)
                plt.title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')
                plt.xlabel('Revenue ($)', fontsize=12)
                plt.ylabel('Product', fontsize=12)
                plt.grid(axis='x', alpha=0.3)
            else:
                # Fallback: bar chart of categorical column
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    value_counts = df[categorical_cols[0]].value_counts().head(10)
                    value_counts.plot(kind='barh', color='coral', edgecolor='black', alpha=0.7)
                    plt.title(f'Top 10 {categorical_cols[0]} Values', fontsize=14, fontweight='bold')
                    plt.xlabel('Count', fontsize=12)
                    plt.ylabel(categorical_cols[0], fontsize=12)

            plt.tight_layout()
            chart_path = os.path.join(output_dir, 'chart_4.png')
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
            print(f"   ✓ Saved chart 4: {chart_path}")
        except Exception as e:
            print(f"   ⚠ Error creating chart 4: {e}")

        # Print summary
        print(f"   ✓ Total charts generated: {len(charts)}")
        print("✅ Visualization Complete\n")

        return {"charts": charts, "count": len(charts), "chart_paths": charts}

    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "charts": []}


def create_visualization_html(chart_paths: list, output_path: str = "results/visualizations.html") -> str:
    """
    Create an HTML file that displays all visualization PNG files

    Args:
        chart_paths: List of paths to PNG chart files
        output_path: Path where HTML file will be saved

    Returns:
        Path to the created HTML file
    """
    print(f"📄 Creating HTML visualization dashboard...")

    # Convert relative paths to relative references for HTML
    chart_images = []
    for i, path in enumerate(chart_paths):
        # Make path relative for HTML
        rel_path = os.path.relpath(path, os.path.dirname(output_path))
        chart_images.append(rel_path)

    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Visualization Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                             'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                             sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}

            h1 {{
                text-align: center;
                color: white;
                margin-bottom: 40px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }}

            .chart-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                overflow: hidden;
                position: relative;
            }}

            .chart-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.4);
            }}

            .chart-card img {{
                width: 100%;
                height: auto;
                display: block;
                border-radius: 8px;
            }}

            .chart-number {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: #667eea;
                color: white;
                width: 35px;
                height: 35px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.1em;
                z-index: 10;
            }}

            .footer {{
                text-align: center;
                color: white;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.3);
            }}

            .footer p {{
                font-size: 0.95em;
                opacity: 0.9;
            }}

            @media (max-width: 768px) {{
                h1 {{
                    font-size: 1.8em;
                    margin-bottom: 30px;
                }}

                .grid {{
                    grid-template-columns: 1fr;
                    gap: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Data Visualization Dashboard</h1>

            <div class="grid">
    """

    # Add chart images to HTML
    for i, chart_path in enumerate(chart_images, 1):
        html_content += f"""
                <div class="chart-card">
                    <div class="chart-number">{i}</div>
                    <img src="{chart_path}" alt="Chart {i}" loading="lazy">
                </div>
        """

    html_content += """
            </div>

            <div class="footer">
                <p>Generated with Pandas + Matplotlib</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write HTML file
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"   ✓ HTML dashboard created: {output_path}")
    return output_path
