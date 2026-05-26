# AutoDS: Multi-Agent Data Science Platform

A **local-first** multi-agent data science platform powered by **Azure OpenAI**. AutoDS automates the end-to-end data science workflow through specialized AI agents that collaborate to deliver actionable insights.

## ✅ Current Status (Phase 0-2 Complete)

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ Complete | Setup, Config, Orchestrator Skeleton |
| Phase 1 | ✅ Complete | Data Ingestion Agent (Local + URL) |
| Phase 2 | ✅ Complete | EDA Agent + Reporting with AI Insights |
| Phase 3 | ⏳ In Progress | Memory & Context Integration (ChromaDB) |
| Phase 4 | 🔜 Planned | Data Cleaning & Feature Engineering |
| Phase 5 | 🔜 Planned | Modeling, Evaluation & Explainability |
| Phase 6 | 🔜 Planned | Deployment & Monitoring |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. Initialize the Project

```bash
python autods_cli.py init
```

### 4. Run a Workflow

```bash
# Run EDA on the demo sales dataset
python autods_cli.py run --dataset demo_sales --goal eda_report

# Run EDA on the Titanic dataset (loaded from URL)
python autods_cli.py run --dataset titanic --goal eda_report
```

---

## 📁 Project Structure

```
autods/
├── __init__.py           # Package init
├── config.py             # Configuration management (Pydantic)
├── registry.py           # Dataset registry (loads datasets.yaml)
├── storage.py            # Data loading from files/URLs
├── memory.py             # ChromaDB-based persistent memory
└── agents/
    ├── __init__.py       # Agent exports
    ├── base_agent.py     # Abstract base agent with Azure OpenAI
    ├── ingestion_agent.py # Data loading and schema extraction
    ├── eda_agent.py      # Exploratory data analysis + LLM insights
    ├── reporting_agent.py # Markdown report generation
    └── orchestrator.py   # Central workflow coordinator

autods_cli.py             # Command-line interface
datasets.yaml             # Dataset registry configuration
requirements.txt          # Python dependencies
.env                      # Azure OpenAI credentials (not in repo)
```

---

## 🤖 Agent Architecture

### Orchestrator Agent
Central coordinator that sequences the workflow:
- Accepts `dataset_id` and `goal` parameters
- Routes data between specialized agents
- Logs execution progress and results
- Stores workflow artifacts in memory

### Ingestion Agent
Loads data from various sources:
- Local CSV, Parquet, JSON, Excel files
- Remote URLs (CSV)
- Extracts schema information (dtypes, missing values, memory usage)

### EDA Agent
Performs exploratory data analysis:
- Summary statistics (mean, std, min, max)
- Missing value detection
- Correlation analysis
- Outlier detection (IQR method)
- **AI-Generated Insights** via Azure OpenAI

### Reporting Agent
Generates comprehensive reports:
- Markdown format with tables
- Dataset overview and quality warnings
- Column-level analysis
- AI-generated recommendations

### Memory System (ChromaDB)
Persistent context storage:
- Stores workflow results and insights
- Enables context retrieval for future runs
- Semantic search across stored knowledge

---

## 📊 CLI Commands

```bash
# Initialize project structure
python autods_cli.py init

# List registered datasets
python autods_cli.py datasets

# Show configuration
python autods_cli.py config

# Run a workflow
python autods_cli.py run --dataset DATASET_NAME --goal eda_report
```

---

## 📝 Adding Datasets

Edit `datasets.yaml` to register new datasets:

```yaml
datasets:
  # Local file
  my_data:
    uri: local:./data/my_data.csv
    format: csv
    description: My dataset description

  # Remote URL
  external_data:
    uri: https://example.com/data.csv
    format: csv
    description: External dataset from URL
```

---

## 🏗️ Architecture Principles

- **Local-First**: All processing happens locally; no cloud storage required
- **Azure OpenAI Only**: LLM is the only external service dependency
- **Modular Agents**: Each agent has a single responsibility
- **Persistent Memory**: ChromaDB enables context-aware analysis
- **Deterministic Code**: All data transformations are deterministic Python code
- **LLM for Insights**: AI generates explanations, not execution logic

---

## 📈 Sample Output

Running `python autods_cli.py run --dataset demo_sales --goal eda_report` produces:

```
============================================================
🤖 AutoDS - Multi-Agent Data Science Platform
============================================================
Dataset: demo_sales
Goal: eda_report

[Orchestrator] Starting workflow...
[Ingestion Agent] ✓ Loaded 30 rows, 10 columns
[EDA Agent] ✓ Analysis complete. Found 6 warnings.
[Reporting Agent] ✓ Report saved to: reports/demo_sales_20251201.md

============================================================
✓ Workflow completed successfully!
  Time: 7.60 seconds
  Report: reports/demo_sales_20251201.md
============================================================
```

---

## 🔮 Roadmap

### Phase 3: Memory Integration
- Context injection into LLM prompts
- Memory retrieval before each agent call
- Cross-run learning and recommendations

### Phase 4: Data Cleaning & Feature Engineering
- Rule-based cleaning agent
- Feature transformation pipelines
- LLM-generated cleaning explanations

### Phase 5: Modeling & Explainability
- scikit-learn model training
- SHAP/LIME explainability
- Hyperparameter tuning

### Phase 6: Deployment
- FastAPI model serving
- Prediction logging
- Drift detection

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM backend
- [ChromaDB](https://www.trychroma.com/) - Vector database for memory
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
