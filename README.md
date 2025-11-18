# Claude Hackathon 🔬

## Multi-Agent Data Analysis Engine

A powerful, intelligent data analysis platform that leverages Claude AI and parallel agent execution to transform raw datasets into stunning, actionable business intelligence reports.

Upload any CSV file and get instant insights from 3 specialized AI agents running in isolated sandboxes, complete with beautiful interactive visualizations and executive summaries.

---

## What It Does

1. **Parallel Agent Execution** - 3 specialized agents analyze your data simultaneously:
   - 📊 **Statistical Analysis Agent** - Computes correlations, distributions, and key metrics
   - 📈 **Visualization Agent** - Generates 4 publication-ready charts
   - 🔍 **Anomaly Detection Agent** - Identifies outliers and data quality issues

2. **AI-Powered Insights** - Claude synthesizes findings into executive summaries, actionable recommendations, and risk assessments

3. **Stunning Reports** - Modern, interactive HTML reports with:
   - Glassmorphic UI with dark/light mode
   - Draggable, expandable floating charts
   - Collapsible insight sections
   - Real-time KPI dashboard
   - Smooth animations throughout

---

## Technical Architecture

### Core Stack
- **Python 3.8+** - Main orchestrator
- **Claude AI (Anthropic)** - Intelligent analysis & synthesis via API
- **E2B Sandboxes** - Isolated Python execution environments
- **Pandas/Matplotlib** - Data processing & visualization
- **Vanilla JavaScript/CSS3** - Interactive front-end (no external dependencies)

### How It Works

```
Your CSV File
     ↓
[Parallel Execution in E2B Sandboxes]
     ├─→ Statistical Agent (generates stats)
     ├─→ Visualization Agent (creates charts)
     └─→ Anomaly Agent (detects issues)
           ↓
    [Claude Coordinator Agent]
         (synthesizes findings)
           ↓
    [Beautiful Report Generation]
    (HTML + CSS + JavaScript)
           ↓
    analysis_report.html
```

### Key Features

**Agent Communication**
- Each agent runs in an isolated E2B sandbox for security
- Claude generates analysis code dynamically based on dataset structure
- Results flow through a coordinator agent for synthesis

**Intelligent Report Generation**
- Parses AI insights into structured, collapsible sections
- Automatically generates KPI cards from analysis results
- Embeds visualizations as interactive floating objects

**Modern UI/UX**
- No external frameworks—pure HTML5/CSS3/JavaScript
- Glassmorphism design with animated background particles
- Dark mode with localStorage persistence
- Fully responsive (desktop, tablet, mobile)

---

## Quick Start

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd claude-hackathon

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export E2B_API_KEY="your-key-here"
```

### Usage

```bash
# Run the analysis pipeline
python3 main.py

# Open the generated report
open results/analysis_report.html
```

That's it! The system will:
1. Analyze your test dataset (`test_data/sales_data.csv`)
2. Run all agents in parallel
3. Generate insights and visualizations
4. Create a stunning interactive report

---

## Project Structure

```
├── main.py                          # Main orchestrator
├── agents/
│   ├── statistical.py              # Statistical analysis agent
│   ├── visualization.py            # Chart generation agent
│   ├── anomaly.py                  # Anomaly detection agent
│   └── coordinator.py              # AI insight synthesizer
├── test_data/
│   └── sales_data.csv             # Sample dataset
└── results/
    ├── analysis_report.html        # Main interactive report
    ├── visualizations.html         # Standalone viz dashboard
    ├── chart_*.png                 # Generated charts
    └── raw_results.json            # Raw analysis data
```

---

## Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Engine | Claude 3.5 Sonnet | Intelligent analysis & synthesis |
| Execution | E2B Sandboxes | Secure, isolated code execution |
| Backend | Python 3.8+ | Orchestration & data processing |
| Data Libs | Pandas, NumPy, SciPy | Statistical computation |
| Viz Libs | Matplotlib | Chart generation |
| Frontend | HTML5/CSS3/JavaScript | Interactive reports |

---

## Report Features

### Interactive Elements
- **Draggable Charts** - Click and drag charts around the canvas
- **Fullscreen Mode** - Expand any chart to fullscreen (⛶)
- **Collapsible Sections** - Expand/collapse insights on demand
- **Dark Mode Toggle** - 🌙 button in top-right corner
- **Smooth Animations** - Glassmorphic fade-ins and transitions

### Content Sections
1. **Header** - Title, generation timestamp, agent/visualization count
2. **KPI Dashboard** - 4 key metrics cards
3. **Executive Insights** - AI-synthesized summary, findings, recommendations
4. **Data Visualizations** - 4 interactive charts
5. **Detailed Analysis** - Statistical breakdown
6. **Data Quality Assessment** - Quality score and anomaly details

---

## Use Cases

- 📊 **Business Intelligence** - Analyze sales, customer, or operational data
- 🔬 **Research** - Process experimental or observational datasets
- 📈 **Startups** - Quick data insights without hiring data scientists
- 🎓 **Education** - Learn how multi-agent AI systems work
- 💼 **Consultants** - Deliver stunning reports to clients instantly

---

## Performance

- **Parallel Execution** - All 3 agents run simultaneously (~30-80 seconds total)
- **Report Generation** - Sub-second HTML/CSS generation
- **Scalability** - Handles datasets with 1000-100K+ rows
- **Sandbox Isolation** - Each agent runs in secure, isolated environment

---

## Limitations & Future Work

### Current Limitations
- Chart generation limited to 4 standard visualizations
- Insights limited to 500 characters per section in some views
- Date parsing requires standard formats

### Roadmap
- [ ] Custom chart types based on data structure
- [ ] Export to PDF, PowerPoint, Excel
- [ ] Real-time collaboration features
- [ ] Custom prompt engineering per dataset type
- [ ] Integration with databases (PostgreSQL, BigQuery, etc.)

---

## Built With 💜

- **Claude AI** - The brains of the operation
- **E2B Sandboxes** - Secure execution environments
- **Python Community** - Pandas, Matplotlib, and friends
- **Modern Web Standards** - No bloated frameworks

---

## License

MIT

---

## Questions?

This project demonstrates the power of multi-agent AI systems combined with secure code execution. Perfect for building intelligent automation, data analysis tools, or AI-powered applications.

Happy analyzing! 🚀
