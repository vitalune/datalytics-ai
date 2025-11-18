# Claude Hackathon 🔬

## Multi-Agent Data Analysis Engine

A powerful, intelligent data analysis platform that leverages Claude AI and parallel agent execution to transform raw datasets into stunning, actionable business intelligence reports.

Upload any CSV file and get instant insights from 3 specialized AI agents running in isolated sandboxes, complete with beautiful interactive visualizations and executive summaries.

[View the Demo](https://vitalune.github.io/datalytics-ai/results/analysis_report.html)

[GitHub Repo](https://github.com/vitalune/datalytics-ai)
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

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Engine | Claude 4.5 Sonnet & Claude 4.5 Haiku| Intelligent analysis & synthesis |
| Execution | E2B Sandboxes | Secure, isolated code execution |
| Backend | Python 3.12+ | Orchestration & data processing |
| Data Libs | Pandas, NumPy, SciPy | Statistical computation |
| Viz Libs | Matplotlib | Chart generation |
| Frontend | HTML5/CSS3/JavaScript | Interactive reports |

---

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

## Use Cases

- **Business Intelligence** - Analyze sales, customer, or operational data
- **Research** - Process experimental or observational datasets
- **Startups** - Quick data insights without hiring data scientists
- **Education** - Learn how multi-agent AI systems work
- **Consultants** - Deliver stunning reports to clients instantly

---

## Performance

- **Parallel Execution** - All 3 agents run simultaneously (~30-80 seconds total)
- **Report Generation** - Sub-second HTML/CSS generation
- **Scalability** - Handles datasets with 1000-100K+ rows
- **Sandbox Isolation** - Each agent runs in secure, isolated environment

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

Contact: amirvalizadeh161@gmail.com

Happy analyzing! 🚀
