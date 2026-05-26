<<<<<<< HEAD
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
=======
# Data Science Agent — Complete Implementation Specification

> **Framework:** Microsoft Agent Framework 1.0 (Python)
> **Scope:** End-to-end autonomous Data Science and Generative AI workloads
> **Format:** Step-by-step guidance document — implementation reference only

---

## How to Read This Document

This document is structured as a phased, sequential implementation guide. Each phase builds on the previous one. Each section tells you **what to build**, **why it matters**, **what decisions to make**, and **what to verify before moving on**. No phase should be skipped. Within each phase, steps are ordered by dependency — complete them in the order written.

---

## Table of Contents

1. [Foundational Concepts You Must Understand First](#1-foundational-concepts-you-must-understand-first)
2. [Architecture Overview](#2-architecture-overview)
3. [Agent Catalogue and Responsibilities](#3-agent-catalogue-and-responsibilities)
4. [MCP Design — Tracking and Tool Servers](#4-mcp-design--tracking-and-tool-servers)
5. [Session Management with Streamable HTTP](#5-session-management-with-streamable-http)
6. [Middleware Pipeline Design](#6-middleware-pipeline-design)
7. [Hooks Registry](#7-hooks-registry)
8. [Code Execution, Auto-Fix, and Debug Loop](#8-code-execution-auto-fix-and-debug-loop)
9. [Browser-Use Integration](#9-browser-use-integration)
10. [DuckDuckGo Deep Research Integration](#10-duckduckgo-deep-research-integration)
11. [Deep Learning and Generative AI Scenario Coverage](#11-deep-learning-and-generative-ai-scenario-coverage)
12. [Phase 1 — Foundation and Scaffolding](#12-phase-1--foundation-and-scaffolding)
13. [Phase 2 — Data Pipeline Agents](#13-phase-2--data-pipeline-agents)
14. [Phase 3 — Model Training and Tuning Agents](#14-phase-3--model-training-and-tuning-agents)
15. [Phase 4 — Explainability, Reporting, and Deployment](#15-phase-4--explainability-reporting-and-deployment)
16. [Phase 5 — Memory, Knowledge, and Retrospection](#16-phase-5--memory-knowledge-and-retrospection)
17. [Phase 6 — Observability, Safety, and Hardening](#17-phase-6--observability-safety-and-hardening)
18. [Phase 7 — End-to-End Validation and Production Readiness](#18-phase-7--end-to-end-validation-and-production-readiness)
19. [Directory and File Structure](#19-directory-and-file-structure)
20. [Configuration Reference](#20-configuration-reference)
21. [Security and Responsible AI Checklist](#21-security-and-responsible-ai-checklist)
22. [Verification Checklist per Phase](#22-verification-checklist-per-phase)

---

## 1. Foundational Concepts You Must Understand First

Before writing a single file, read and internalise these concepts. Implementation decisions throughout this document depend on them.

### 1.1 Microsoft Agent Framework 1.0

The Microsoft Agent Framework (hereafter "the Framework") is the direct successor to both AutoGen and Semantic Kernel. It is built by the same Microsoft teams and unifies AutoGen's simple agent abstractions with Semantic Kernel's enterprise features — session-based state management, type safety, telemetry, and middleware — under one library.

The Framework provides four stable primitives you will use everywhere:

- **Agent** — a named entity that wraps an LLM call, a system prompt, a set of tools, and a list of MCP servers. Once created, an agent is referenced by its name or ID.
- **Session** — a stateful, running instance of an agent. Sessions maintain conversation history, persist tool results, and can be long-lived across multiple exchanges.
- **Workflow** — a graph-based engine that connects multiple agents and plain functions as nodes, with typed edges representing dependencies and routing logic. Workflows give you explicit, reproducible control over multi-agent execution order.
- **Middleware** — a pipeline of interceptors that wrap every agent action. Middleware fires before and after every run, before and after every tool call, and on every error.

The Framework supports Azure Foundry, Azure OpenAI, OpenAI, Anthropic Claude, Amazon Bedrock, Google Gemini, and Ollama as model providers.

### 1.2 MCP Protocol Version 2025-06-18

The Model Context Protocol (MCP) is the standard your agents use to discover and call external tools. The current required version is **2025-06-18**, which uses **Streamable HTTP** as its transport. Earlier implementations used Server-Sent Events (SSE). If you are deploying to any remote environment (Azure Container, Cloud Run, AWS Fargate), Streamable HTTP is mandatory.

Key protocol requirements for Streamable HTTP:

- The MCP server must expose its root at the path `/`
- The server must support the `HEAD` method on that root path for protocol discovery
- Session management uses the `Mcp-Session-Id` header, which the server assigns at initialisation and the client must echo on all subsequent requests
- HTTP status codes are semantic signals: returning `501 Not Implemented` on a GET tells the client the server is broken; returning `405 Method Not Allowed` with an `Allow: POST` header tells the client it is a POST-only server by design

### 1.3 Claude Managed Agents and Session Lifecycle

Claude Managed Agents (Anthropic's managed infrastructure) exposes a session model that you will mirror in the Microsoft Agent Framework. Understanding it clarifies the patterns this document asks you to implement.

The lifecycle is: create an agent definition once → create an environment → start a session → send events → receive streamed results via SSE → optionally send mid-session guidance or interrupts → session ends when the task is complete or you terminate it. Session history is persisted server-side and is fetchable in full.

Apply this same lifecycle model to your Microsoft Agent Framework sessions. Agent definitions are reusable. Sessions are ephemeral but their state is durable.

### 1.4 Browser-Use

Browser-Use is an open-source library (and cloud service) that gives an LLM agent the ability to interact with websites like a human — navigating, clicking, reading DOM content, filling forms, and extracting data. You will use it in two modes:

- **Local mode** — running a headless Chromium browser controlled by Browser-Use, driven by an LLM you supply. Use this for documentation crawling and error debugging.
- **Cloud/Sandbox mode** — Browser-Use's hosted cloud handles the browser instance, auth, cookies, and anti-detect profiles. Use this for any production task that requires persistent login state or resilience.

The agent accepts a natural-language task description and an LLM client. It exposes step-by-step streaming (you can iterate over steps as they happen) and a final result object.

### 1.5 A2A Protocol

The Agent-to-Agent (A2A) protocol, now governed by the Linux Foundation, defines how agents built in different frameworks discover each other, exchange messages, and coordinate tasks. The Microsoft Agent Framework has A2A support landing in a near-term update. Design your inter-agent communication with A2A in mind now so migration is seamless.

---

## 2. Architecture Overview

### 2.1 System Topology

The system is a directed graph of specialised agents, all coordinated by a central Orchestrator Agent. The Orchestrator owns the Workflow Graph and is the only agent that can spawn other agents or change the execution path. All other agents are leaf workers that receive a task, use their tools, return an output artifact, and terminate.

Two MCP servers sit as a shared infrastructure layer accessible to all agents:

- The **Tracking MCP Server** records every agent start, end, tool call, artifact URI, error, and retry. It is the system's audit log and the Orchestrator's source of truth.
- The **DS Tools MCP Server** exposes all data science tools as MCP-callable endpoints. Agents do not call tools directly through Python imports — they call them through MCP so that every tool invocation is logged, rate-limited, and retryable.

A **Code Sandbox** (Docker container or Azure Container Instance) is the only environment where generated code actually runs. No agent executes code in its own process. Code always goes through the sandbox.

### 2.2 Data Flow

Every pipeline run follows this data flow:

Raw data source → Ingestion Agent → Azure Blob Storage (raw snapshot) → EDA Agent → Cleaning Agent → Feature Engineering Agent → Model Training Agent → Hyperparameter Tuning Agent → Evaluation Agent → Explainability Agent → Report Agent → Deployment Agent → Monitoring Agent

The Memory Agent does not sit in the linear flow. It is a subscriber that receives notification from the Orchestrator after every stage completes and indexes all produced artifacts.

### 2.3 Key Design Decisions

Make these decisions before writing any code and document them in a Decision Log file:

- **Which Azure region?** All Azure resources must be in the same region to minimise latency and avoid cross-region data transfer costs.
- **Which model for which agent?** Reasoning-intensive agents (Orchestrator, Debug Agent) should use the most capable model available. Tool-heavy agents with short prompts can use a smaller, faster model.
- **Sandbox isolation level?** Docker with `network_mode=none` is the minimum. Azure Container Instance with a private VNet is the production recommendation.
- **Synchronous or asynchronous pipeline?** For interactive use, synchronous with streaming is appropriate. For overnight batch runs, asynchronous with webhooks is more appropriate. Design the Orchestrator to support both.

---

## 3. Agent Catalogue and Responsibilities

Each agent listed here has a single, well-defined responsibility. Do not give any agent responsibilities that belong to another. If you find yourself adding a second distinct responsibility to an agent, split it into two agents.

### 3.1 Orchestrator Agent

The Orchestrator is the only agent with authority over the workflow graph. It parses the user's task into pipeline stages, maps stages to agents, invokes them in dependency order using the Workflow engine, monitors each agent's progress via the Tracking MCP Server, and reroutes on failure. It never executes data science logic itself.

When a stage fails, the Orchestrator must: receive the failure event from the Tracking MCP Server, route the failed code and error to the Debug Agent, wait for the repaired output, retry the failed stage with the repaired input, and increment a retry counter. After five consecutive failures on the same stage, the Orchestrator escalates to the user via a human-in-the-loop gate.

The Orchestrator is also responsible for defining the checkpoint policy. After each stage completes successfully, it writes a checkpoint to the Tracking MCP Server so that a crashed pipeline can resume from the last completed stage rather than restarting from scratch.

### 3.2 Data Ingestion Agent

This agent's sole job is to connect to a data source, pull the data, validate it, and persist a snapshot.

It must be able to read from: local CSV and Parquet files, PostgreSQL and other ANSI SQL databases via a connection string, Azure Data Lake Storage Gen2, Azure Blob Storage, REST API endpoints with JSON responses, and Excel files.

Validation means: confirming the schema matches expectations (if a schema was provided), confirming the row count is within expected bounds, computing per-column null ratios, and detecting obviously malformed rows (wrong number of delimiters, binary content in text fields). Validation results are logged to the Tracking MCP Server.

The snapshot is written to Azure Blob Storage with a versioned path that includes the run ID and a UTC timestamp. The snapshot URI is the primary output artifact of this agent.

### 3.3 EDA Agent

This agent produces a comprehensive characterisation of the data. It receives the raw snapshot URI from the Ingestion Agent and produces an EDA report object.

The EDA report must include: descriptive statistics for all columns (mean, median, standard deviation, min, max, quartiles, skew, kurtosis), null counts and null percentages per column, cardinality counts for categorical columns, class distribution for any identified target column, a correlation matrix, and a list of any columns that appear to have data quality issues.

Visualisations must be produced for: histograms for all numeric columns, box plots for numeric columns to reveal outliers, a correlation heatmap, and a class balance chart if a target column exists. Each visualisation is saved to Azure Blob Storage and its URI is recorded.

The natural-language narrative is generated by calling Azure OpenAI with all computed statistics and a prompt that asks for a plain-English interpretation of the data, flagging the most important issues and patterns.

### 3.4 Data Cleaning Agent

This agent detects quality issues and applies corrective transformations. It must not silently drop data — every transformation decision must be logged with its justification.

The cleaning process follows a fixed chain of thought that the agent's system prompt enforces. The steps are:

First, enumerate all columns with missing values and classify each missing pattern as Missing Completely At Random, Missing At Random, or Missing Not At Random, based on statistical tests. Second, for each missing pattern, select an imputation strategy — median for MCAR numeric columns, mode for MCAR categorical columns, KNN or MICE imputation for MAR or MNAR columns — and justify the choice. Third, detect outliers using IQR and Z-score methods, flag them, and ask the user (via a human-in-the-loop gate) whether to remove, cap, or leave them. Fourth, apply all approved transformations. Fifth, validate the cleaned dataset by recomputing null counts, comparing row count before and after, and confirming no dtype regressions.

The cleaned dataset is stored in Azure Blob Storage with a new version ID, and the transformation log is stored alongside it.

### 3.5 Feature Engineering Agent

This agent generates and selects features. It must recommend features appropriate to the data domain and task type, not just apply a fixed template.

The research step comes first: the agent uses the DuckDuckGo tool to search for domain-specific feature engineering practices relevant to the data. For example, if the data is about credit risk, it searches for standard credit risk features. The results inform the feature recommendations.

Feature creation includes: polynomial and interaction terms for numeric columns, one-hot encoding for low-cardinality categoricals, target encoding for high-cardinality categoricals, ordinal encoding for ordered categoricals, log and power transforms for skewed numeric distributions, and sentence embeddings for free-text columns using a hosted embedding model.

Feature selection uses a quick RandomForest run (100 trees, no tuning) to compute feature importance. Features below a configurable importance threshold are dropped. The agent produces a `feature_manifest` artifact that documents every original column, every new feature, the transform applied, and the importance score.

### 3.6 Model Selection and Training Agent

This agent selects algorithms appropriate to the task type, trains them, and identifies the best baseline model.

Task type detection is the first step. The agent must infer the task type from the target column, the data structure, and the user's description. Task types it must handle: binary classification, multi-class classification, regression, multi-output regression, time-series forecasting, clustering, anomaly detection, and generative AI tasks (text generation, image generation, embedding, retrieval-augmented generation, LLM evaluation).

For classical ML tasks, the agent must attempt at minimum: a linear baseline model (Logistic Regression or Ridge), a tree ensemble (Random Forest, XGBoost, LightGBM, CatBoost), and an SVM with RBF kernel. If Azure AutoML is enabled in configuration, it must also submit an AutoML run.

For deep learning tasks, see Section 11 for the full coverage matrix.

All training runs are logged to Azure ML Experiment Tracker via the `log_experiment` tool. The best model artifact is persisted to Azure Blob Storage.

### 3.7 Hyperparameter Tuning Agent

This agent takes the best model from the Model Selection Agent and applies systematic hyperparameter optimisation.

For sklearn and XGBoost/LightGBM models, use Optuna inside the code sandbox. For PyTorch models, use Optuna combined with Ray Tune inside the sandbox. For Azure-managed runs, use Azure ML HyperDrive.

The agent must define a search space appropriate to the model type, not a generic one. The search space for an XGBoost model is different from the search space for a neural network. Document the search space decisions in the Tracking MCP Server.

The output is a `best_params` artifact and a `tuning_report` artifact. The tuning report shows the top-N configurations, their metric values, and the convergence plot (saved as a chart in Blob Storage).

### 3.8 Evaluation and Validation Agent

This agent computes all relevant metrics, runs fairness checks, and checks for data drift.

Metrics must be selected automatically based on task type. Classification tasks require accuracy, precision, recall, F1 (macro and weighted), ROC-AUC, precision-recall AUC, Matthews Correlation Coefficient, and a confusion matrix. Regression tasks require RMSE, MAE, R², MAPE, and Huber Loss. Time-series forecasting tasks require MASE, SMAPE, and coverage (for probabilistic forecasts). Deep learning tasks require loss curves, gradient norm tracking, and attention maps where applicable.

Fairness analysis uses Fairlearn. The agent must ask the user to identify any protected attributes (age, gender, race, etc.) and compute demographic parity and equalized odds against those attributes.

Data drift detection uses Kolmogorov-Smirnov tests and Population Stability Index to compare the training distribution against the validation or held-out distribution. Drift alerts are flagged in the evaluation report.

### 3.9 Explainability Agent

This agent produces both technical explanations (SHAP values, LIME explanations, attention maps) and plain-English explanations suitable for non-technical stakeholders.

For tree-based models, use SHAP TreeExplainer. For linear models, use SHAP LinearExplainer. For PyTorch models, use SHAP DeepExplainer and Captum's Integrated Gradients. For vision models, use GradCAM via Captum. For text models, use LIME's text explainer. For tabular models, use LIME's tabular explainer.

All plots are saved to Azure Blob Storage. The plain-English explanation is generated by Azure OpenAI with a prompt that receives the top-N SHAP features and asks for a non-technical narrative.

If the SHAP version installed in the sandbox conflicts with the model type, the agent invokes Browser-Use to browse the SHAP documentation for the correct API.

### 3.10 Report and Dashboard Agent

This agent assembles all artifacts produced by previous agents into a final report.

The report must contain: an executive summary, the EDA narrative, the cleaning decisions log, the feature manifest summary, a model comparison table (all algorithms tried with their metrics), the best model's evaluation metrics, fairness analysis results, SHAP plots with explanations, the top features ranked by importance, and a model card section describing training data, known limitations, and intended use.

Output formats: a Markdown file, an HTML file with inline base64 charts, and optionally a Power BI dataset push via the Power BI REST API. All output files are stored in Azure Blob Storage and their URIs are registered in the Tracking MCP Server.

### 3.11 Deployment and Monitoring Agent

This agent packages the best model as a deployable endpoint and configures monitoring.

Packaging steps: serialise the model (pickle for sklearn, ONNX for cross-framework compatibility, TorchScript for PyTorch production), wrap it in a FastAPI application with input schema validation via Pydantic, write a Dockerfile that bundles the model file and the API, and build the container image.

Deployment target: Azure Container Instance for initial deployment. Azure Kubernetes Service for high-availability production deployments. The deployment target is a configuration choice.

After deployment: run a smoke test with ten sample inputs from the training data and verify that the response schema matches expectations. Configure Azure Monitor alerts for latency (P99 exceeding 500ms), error rate (exceeding 1%), and prediction drift (detected by daily KS test job in Azure ML).

### 3.12 Memory and Knowledge Agent

This agent runs after every pipeline stage and after every full pipeline completion. It is not invoked by the linear workflow — it is subscribed as an observer to the Tracking MCP Server's event stream.

It indexes all artifacts into Azure Cognitive Search. Each indexed document contains: run ID, pipeline stage, artifact type, artifact URI, key metrics, model type, dataset name, task type, and timestamp.

It maintains a lineage graph in Cosmos DB that maps each artifact to its upstream dependencies. You can query the lineage to answer questions like "what training data produced this model?" or "which feature manifest was used for this experiment?".

The agent exposes a natural-language query interface powered by RAG: embed the query, search the Cognitive Search index, retrieve the top documents, and use Azure OpenAI to synthesise a grounded answer.

### 3.13 Debug Agent

This agent is not invoked by the user. It is invoked by the Orchestrator or the Code Execution system whenever a code execution fails.

The Debug Agent's only job is to analyse an error and return repaired code. It has no authority to modify pipeline state, change configuration, or skip stages.

Its resolution strategy follows five attempts in order:

- Attempt one: pattern-match the error against a known error catalogue and apply a pre-defined fix strategy
- Attempt two: invoke Browser-Use to crawl the relevant library's official documentation for the error
- Attempt three: invoke DuckDuckGo to search GitHub Issues and Stack Overflow for the exact error message
- Attempt four: ask the LLM to reason from first principles about the error and the code structure
- Attempt five: rewrite the failing section from scratch using a different technical approach

After five failed attempts, the Debug Agent writes a full debug report (original code, all repair attempts, all error outputs, all documentation found) and escalates to the Orchestrator, which triggers a human-in-the-loop gate.

---

## 4. MCP Design — Tracking and Tool Servers

### 4.1 Tracking MCP Server

This server is the system's nervous system. Every agent action writes to it; the Orchestrator reads from it.

The server must expose these capabilities as MCP tools:

- `record_agent_start` — accepts agent name, run ID, stage name, input artifact URIs, and a timestamp
- `record_agent_end` — accepts agent name, run ID, stage name, output artifact URIs, duration in milliseconds, and status (success or failure)
- `record_tool_call` — accepts agent name, tool name, tool input hash, tool output hash, and duration
- `record_artifact` — accepts artifact URI, artifact type, artifact metadata, and the run ID that produced it
- `record_error` — accepts agent name, error type, error message, traceback, and attempt number
- `record_checkpoint` — accepts run ID and stage name; marks this stage as completed so restarts can skip it
- `query_run_history` — returns all stages completed for a given run ID
- `query_best_model` — accepts task type and metric name; returns the artifact URI of the best model ever recorded for that task type and metric
- `query_artifact_lineage` — returns the full dependency chain for a given artifact URI

The Tracking MCP Server must persist to a durable store (Azure Cosmos DB or PostgreSQL) so that history survives restarts.

### 4.2 DS Tools MCP Server

This server exposes all data science tools as callable MCP endpoints. Agents never import these tools as Python libraries directly — they always call them via MCP so that logging, rate-limiting, and retry are applied uniformly.

Tools to expose:

- `run_code` — submit code to the sandbox, return stdout, stderr, exit code, and artifact URIs
- `query_sql` — run a SQL query against a registered database connection, return results as JSON
- `read_csv` — read a CSV from a URI and return schema and sample rows
- `read_blob` — read a file from Azure Blob Storage, return content or URI
- `write_blob` — write a file to Azure Blob Storage, return the URI
- `plot_chart` — generate a chart from data, save to Blob Storage, return the URI
- `train_sklearn` — submit a sklearn training job, return metrics and model artifact URI
- `train_pytorch` — submit a PyTorch training job in the sandbox, return metrics and model artifact URI
- `run_shap` — compute SHAP values for a model and dataset, return plot URIs
- `search_docs` — invoke Browser-Use to crawl documentation, return extracted content
- `web_research` — invoke DuckDuckGo to search the web, return result summaries
- `write_blob` — persist any file to Blob Storage
- `query_memory` — query the Cognitive Search index, return matching documents
- `log_experiment` — log metrics and parameters to Azure ML Experiment Tracker and MLflow
- `deploy_endpoint` — package and deploy a model to Azure Container Instance

### 4.3 MCP Server Compliance Checklist

Before considering either MCP server complete, verify:

- The server listens on a root path of `/`
- The root path responds to `HEAD` requests with a 200 status
- Initialisation returns an `Mcp-Session-Id` header
- All subsequent requests include the `Mcp-Session-Id` header
- GET requests to the root return `405 Method Not Allowed` with `Allow: POST` in the response header
- All tool inputs and outputs are typed using JSON Schema
- The server supports concurrent requests without session mixing
- The server returns structured error responses (not bare 500s) when a tool fails

---

## 5. Session Management with Streamable HTTP

### 5.1 Session Architecture

Each pipeline run corresponds to one Orchestrator session. Sub-agent invocations are nested sessions within that Orchestrator session. The session hierarchy is:

Orchestrator Session (run ID) → Stage Sessions (one per agent invocation) → Tool Sessions (one per MCP tool call)

Every level of the hierarchy has its own session ID, and every session ID is propagated downward so that the Tracking MCP Server can reconstruct the full call tree.

### 5.2 Session Lifecycle Steps

Follow these steps precisely when starting any agent session:

Step one — Create the agent definition if it does not already exist. Agent definitions are reusable. Cache the agent ID.

Step two — Start a session by calling the session creation endpoint with the agent ID, the environment configuration, and the initial user event.

Step three — On session creation response, capture and store the session ID. All subsequent interactions with this session must include this session ID.

Step four — Send user events to the session event stream. Receive streamed results via SSE. Buffer and process each event type correctly: assistant messages, tool call requests, tool results, status updates, and error events.

Step five — For each tool call request received in the event stream, execute the tool (via the DS Tools MCP Server), capture the result, and send the result back to the session as a tool result event.

Step six — When the session emits a `status: idle` event, the agent has finished its turn. Capture the final output artifact URIs from the last assistant message.

Step seven — Write a checkpoint to the Tracking MCP Server recording that this stage completed.

Step eight — If the pipeline has more stages, hand the output artifact URIs to the Orchestrator, which routes them to the next agent.

### 5.3 Session Resumability

If a session fails mid-run (network error, timeout, sandbox crash), the Orchestrator must be able to resume without restarting from the beginning.

Implement resumability as follows: before each stage invocation, the Orchestrator queries the Tracking MCP Server for the last completed checkpoint on this run ID. If a checkpoint exists for the about-to-run stage, the Orchestrator skips that stage and advances to the next. This means stages must be idempotent — running a stage twice must produce the same result.

### 5.4 Human-in-the-Loop Gates

Certain decisions must pause the pipeline and wait for a human decision before continuing. Define human-in-the-loop gates at these points:

- After the EDA Agent completes and before the Cleaning Agent starts, to allow the user to review the EDA report and confirm the approach
- After the Cleaning Agent proposes outlier handling strategies, to allow the user to approve or override
- After the Evaluation Agent flags significant fairness violations, to allow the user to decide whether to proceed with deployment
- After the Debug Agent exhausts all five repair attempts, to present the debug report to the user

Implement each gate as a special session event type that pauses the workflow and sends a notification (webhook or email) to the user. The workflow resumes only when the user sends a resume event with their decision.

---

## 6. Middleware Pipeline Design

### 6.1 Middleware Ordering

Middleware layers execute in a specific order on the way in (request) and the reverse order on the way out (response). Define the order in a central configuration file and do not deviate from it. The correct inbound order is:

Logging → Rate Limiting → Safety Check → Retry → Telemetry → Agent

The outbound order (response) is the reverse: Agent → Telemetry → Retry (on error) → Safety Check → Rate Limiting → Logging.

### 6.2 Logging Middleware

Capture structured JSON log entries for every agent invocation. Every log entry must include: timestamp, run ID, session ID, agent name, event type (start, end, tool call, error), input token count, output token count, duration in milliseconds, and status.

Write logs to Azure Monitor via OpenTelemetry. Do not write logs to disk inside the agent process — disk I/O inside an agent session adds latency and is lost on crash.

### 6.3 Rate Limiting Middleware

Apply a token bucket rate limiter per agent per minute. The limits are configurable per agent. The Orchestrator has a higher limit than sub-agents because it makes more frequent, shorter calls. The Training Agent has a lower limit because each call is long and expensive.

When a rate limit is hit, the middleware must: wait for the bucket to refill (do not fail immediately), log the wait event to the Tracking MCP Server, and then proceed. Only after a configurable maximum wait time should the middleware fail the request.

### 6.4 Safety Check Middleware

Inspect every tool call input before it is sent to the DS Tools MCP Server. Block any input that matches known dangerous patterns. The blocked pattern list must include: shell commands that modify the filesystem outside the sandbox (`rm`, `mv`, `cp` applied to paths outside `/workspace`), SQL commands that modify the database schema or drop tables, any attempt to write to environment variables or system configuration files, and any outbound HTTP request from inside the sandbox.

When a blocked pattern is detected, the middleware must: log the violation to the Tracking MCP Server with full context, raise a `SafetyViolationError`, and not retry. Safety violations always escalate to the Orchestrator.

### 6.5 Retry Middleware

Apply exponential backoff with jitter on transient failures. Transient failures are: HTTP 429 (rate limit), HTTP 502/503/504 (upstream unavailable), and any timeout that does not indicate a logic error.

Non-transient failures (HTTP 400, HTTP 401, logic exceptions like `ValueError` or `KeyError`) must not be retried. The middleware must distinguish between these categories.

The retry configuration per agent must specify: maximum retry count, base delay in seconds, jitter range in seconds, and the list of error types considered transient.

### 6.6 Telemetry Middleware

Wrap every agent invocation in an OpenTelemetry span. The span must include: span name (agent name + stage), attributes (run ID, session ID, model name, tool names called), events (each tool call as a span event), and status (OK or ERROR with error message).

Export spans to Azure Application Insights. Use the W3C Trace Context propagation standard so that distributed traces across agents and MCP servers are stitched together into a single trace tree.

---

## 7. Hooks Registry

### 7.1 What Hooks Are

Hooks are finer-grained than middleware. While middleware wraps entire agent invocations, hooks attach to specific named events within an invocation. A hook is a function that receives context about an event and can either pass through, modify the event data, or raise an exception to abort.

Implement hooks as a central registry. Every agent registers which hooks it wants to use from the registry. The registry guarantees that hooks fire in a consistent order regardless of which agent registered them.

### 7.2 Required Hooks

Implement and register all of the following hooks:

`before_code_execute` — fires before any code is submitted to the sandbox. Use this hook to run static analysis (bandit for security, pylint for quality) on the code. If the static analysis finds a high-severity issue, raise an exception to abort the execution. Return the (possibly modified) code to proceed.

`after_code_execute` — fires after a sandbox execution completes, regardless of success or failure. Use this hook to capture any files written to `/workspace/output` inside the sandbox and upload them to Azure Blob Storage. Record the artifact URIs in the Tracking MCP Server.

`before_model_train` — fires before a training job is submitted. Use this hook to verify that a cleaned dataset artifact exists, that the feature manifest exists, and that the GPU quota is available if a GPU is requested. Abort with a clear error message if any precondition is not met.

`after_model_train` — fires after a training job completes. Use this hook to log all metrics to Azure ML Experiment Tracker and MLflow. Also record the model artifact URI and associated metadata in the Tracking MCP Server.

`before_deploy` — fires before a deployment job is submitted. Use this hook to verify that an evaluation report exists and that fairness checks passed. Abort if the evaluation report is missing or if the user has not approved a deployment following a fairness violation.

`after_deploy` — fires after a deployment job completes. Use this hook to run the smoke test (ten sample predictions against the live endpoint) and to record the endpoint URL in the Tracking MCP Server.

`on_error` — fires whenever any agent raises an exception. Use this hook to route the error to the Debug Agent, providing it with the failing code, the error message, the traceback, and the current attempt number.

`on_max_retries_exceeded` — fires when the Debug Agent has exhausted all five repair attempts. Use this hook to write the full debug report to Azure Blob Storage and to trigger the human-in-the-loop gate.

`before_mcp_tool_call` — fires before any MCP tool call is dispatched. Use this hook to apply safety pattern matching against the tool input. This is the hook-level complement to the Safety Check Middleware.

`after_mcp_tool_call` — fires after any MCP tool call returns. Use this hook to record the tool call in the Tracking MCP Server and to verify that the tool output schema matches expectations.

---

## 8. Code Execution, Auto-Fix, and Debug Loop

### 8.1 Sandbox Design

The sandbox is the only environment where generated code runs. It must be a Docker container built from a custom image that includes all data science libraries pre-installed. The sandbox must have:

- No outbound network access (`network_mode=none` in Docker). Libraries are pre-installed in the image; there is no `pip install` at runtime.
- A read-only mount for input data files
- A read-write mount for output artifacts, scoped to `/workspace/output`
- A memory limit (4 GB default, configurable)
- A CPU limit (2 cores default, configurable)
- A wall-clock timeout (300 seconds default, configurable)

The sandbox image must include Python with all standard data science libraries (pandas, numpy, scikit-learn, xgboost, lightgbm, catboost, matplotlib, seaborn, plotly, shap, lime, optuna, torch, torchvision, transformers, datasets, sentence-transformers, captum) all pinned to specific versions.

### 8.2 Auto-Fix Loop Sequence

When code execution fails, execute the following sequence:

Step one — Capture the complete stderr output, the exit code, and the last line of stderr (which is usually the error type and message).

Step two — Call `on_error` hook, which routes to the Debug Agent with the captured information plus the original code and the current attempt number.

Step three — The Debug Agent returns repaired code.

Step four — If the repaired code is identical to the failed code, the Debug Agent has given up. Do not retry with identical code. Proceed directly to escalation.

Step five — Replace the current code with the repaired code and re-execute in the sandbox.

Step six — Repeat steps one through five, incrementing the attempt counter, until either a run succeeds or the attempt counter reaches five.

Step seven — On five consecutive failures, call `on_max_retries_exceeded` hook.

### 8.3 Debug Agent Resolution Strategies

The Debug Agent applies these strategies in order, advancing to the next only if the previous produced code that still fails:

**Known error pattern matching** — maintain a catalogue of common errors and their fixes. Examples: `ModuleNotFoundError` for a library that is in the image but not imported correctly, `CUDA out of memory` errors (halve batch size, enable gradient checkpointing), `KeyError` on a column name (check the feature manifest for correct column names), `ValueError: could not convert string to float` (add type conversion before the operation), `MemoryError` (switch to chunked processing).

**Documentation crawling via Browser-Use** — form a search query from the error type, the error message, and the library name inferred from the traceback. Use Browser-Use to navigate to the library's official documentation and extract the relevant section. Present the extracted content plus the original code and error to the LLM and ask for a repair.

**GitHub Issues and Stack Overflow search via DuckDuckGo** — search for the exact error message plus the library name. Retrieve the top five results. Present the results plus the original code and error to the LLM and ask for a repair.

**First-principles LLM reasoning** — present the original code, the full traceback, and a prompt that asks the LLM to reason step by step about what the code is attempting, where the error occurs, and what the correct fix is. Do not provide any search results at this step — pure reasoning only.

**Complete rewrite with different approach** — present the original task description (not the failed code) and the error context to the LLM and ask it to solve the same task using a completely different technical approach.

---

## 9. Browser-Use Integration

### 9.1 When to Use Browser-Use

Browser-Use is invoked in exactly two situations:

- When the Debug Agent needs to crawl library documentation to understand an error (see Section 8.3, strategy two)
- When the Feature Engineering Agent needs to research domain-specific feature practices

Do not use Browser-Use for general web search. DuckDuckGo handles general search. Browser-Use handles documentation crawling that requires navigating multi-page sites, following links, and extracting structured content from JavaScript-rendered pages.

### 9.2 Configuration

Browser-Use must be configured to use the same Azure OpenAI model that powers your agents. This ensures consistent reasoning quality and avoids API key proliferation.

Configure Browser-Use in local mode for development and in sandbox/cloud mode for production. In local mode, Browser-Use controls a local Chromium instance. In cloud mode (browser-use cloud), Browser-Use's infrastructure manages the browser with anti-detect profiles and persistent authentication state.

Set `headless=True` in all environments. Set `max_steps` to a value appropriate for the complexity of the documentation site (50 steps is a reasonable upper bound for most library docs).

### 9.3 Documentation Site Registry

Maintain a registry that maps Python library names to their official documentation URLs. When the Debug Agent determines which library caused an error (from the traceback), it looks up the documentation URL from this registry and passes it to Browser-Use as the starting URL.

The registry must cover at minimum: pandas, numpy, scikit-learn, xgboost, lightgbm, catboost, torch, torchvision, transformers (Hugging Face), datasets (Hugging Face), sentence-transformers, shap, lime, captum, optuna, azure-ai-ml (Azure ML SDK v2), and azure-storage-blob.

### 9.4 Browser-Use Output Handling

Browser-Use returns a result object with a `final_result` field containing the extracted text. This text is passed to the Debug Agent's LLM along with the failed code and the error. The Browser-Use result text must be truncated to a maximum of 4,000 characters before inclusion in the LLM prompt to avoid context window overflow.

If Browser-Use fails to find relevant content (the result is empty or off-topic), log the failure and advance to DuckDuckGo search. Do not retry Browser-Use on the same query.

### 9.5 Production Deployment of Browser-Use

In production, use Browser-Use's `@sandbox` decorator pattern to run the browser agent inside a Browser-Use cloud sandbox. This gives you: the browser running adjacent to the agent (minimal latency), persistent login state via cloud browser profiles, and resilience against browser crashes. Store the cloud profile ID in your environment configuration.

---

## 10. DuckDuckGo Deep Research Integration

### 10.1 When to Use DuckDuckGo

DuckDuckGo search is invoked in three situations:

- When the Debug Agent needs to search GitHub Issues and Stack Overflow for an error message (see Section 8.3, strategy three)
- When the Feature Engineering Agent needs to research best practices for domain-specific features
- When the Model Selection Agent needs to research which algorithms or architectures perform best on a specific problem type

### 10.2 Query Construction

DuckDuckGo queries must be constructed carefully to return useful results. Apply these rules:

For debugging queries: include the exact error type, the library name, and the Python version. Add `site:stackoverflow.com OR site:github.com` to focus on relevant sources.

For feature engineering research queries: include the domain name (e.g., "credit risk", "medical imaging", "time series electricity demand"), the word "features", and the year (to bias toward recent results).

For algorithm research queries: include the problem description, benchmark terms ("SOTA", "benchmark", "comparison"), and the data modality (tabular, image, text, time series).

### 10.3 Rate Limiting

Apply a global rate limit of 30 DuckDuckGo searches per hour across the entire system. This is enforced by the DS Tools MCP Server, which tracks all `web_research` tool calls.

If the rate limit is reached, the tool must return a rate limit error and the calling agent must fall back to its next resolution strategy (do not wait and retry, as the pipeline would stall).

### 10.4 Result Processing

DuckDuckGo returns a list of result objects, each with a title, URL, and snippet. The top ten results are passed to the LLM in the format: `[1] Title\nURL\nSnippet`. The LLM must be instructed to cite which result informed its repair suggestion.

Do not pass raw HTML to the LLM. Only pass the structured result objects.

---

## 11. Deep Learning and Generative AI Scenario Coverage

### 11.1 Scenario Detection

Before selecting any algorithm or architecture, the Orchestrator must ask the Model Selection Agent to classify the task into one of the following scenario types. The scenario type determines the template, the training loop configuration, and the evaluation metrics.

Classical ML scenarios: binary classification, multi-class classification, single-output regression, multi-output regression, clustering (unsupervised), anomaly detection, ranking.

Deep Learning scenarios: image classification, object detection, image segmentation, image generation (diffusion / GAN), text classification, token classification (NER, POS tagging), question answering, text generation (autoregressive LM fine-tuning), sequence-to-sequence (summarisation, translation), tabular deep learning (TabNet, FT-Transformer), time series forecasting (LSTM, Transformer, N-BEATS, PatchTST), recommendation (Neural Collaborative Filtering, Two-Tower).

Generative AI scenarios: retrieval-augmented generation (RAG) system construction, embedding model fine-tuning, LLM evaluation (RAGAS framework, LLM-as-judge), multimodal (CLIP, LLaVA), agent tool use fine-tuning.

### 11.2 Non-Negotiable Training Loop Requirements

For every deep learning training job, the generated code must address every item in this checklist. The `before_model_train` hook must verify this checklist is addressed before allowing the training job to proceed.

Data pipeline: a proper DataLoader with configurable batch size, appropriate augmentation for the data modality, normalisation matching the pre-trained model's expected statistics if a pre-trained model is used, and class weighting or oversampling if class imbalance is detected.

Model architecture: clearly defined input shape, clearly defined output shape matching the task, appropriate activation functions, dropout for regularisation, batch normalisation for deep networks.

Loss function: task-appropriate (cross-entropy for classification, MSE or Huber for regression, focal loss for imbalanced classification, contrastive or triplet loss for embedding, etc.).

Optimiser: AdamW with weight decay as the default. Document the justification if a different optimiser is chosen.

Learning rate scheduling: at minimum one of CosineAnnealingLR, OneCycleLR, or ReduceLROnPlateau. The choice must be documented.

Mixed precision training: enabled via the appropriate library mechanism when a GPU is available.

Gradient clipping: applied with a maximum norm of 1.0 by default.

Early stopping: implemented with a configurable patience (default 10 epochs) and minimum delta (default 1e-4).

Checkpointing: save the model with the best validation metric at each epoch. Resume from the best checkpoint at the end of training.

GPU memory management: clear the GPU cache at the start of each epoch. Use gradient accumulation if the configured batch size causes out-of-memory errors.

Reproducibility: set random seeds for Python, NumPy, PyTorch, and CUDA at the start of every training run. Log the seed value.

Logging: record training loss, validation loss, and the primary metric at every epoch. Log to Azure ML Experiment Tracker.

### 11.3 Deep Learning Auto-Remediation

When a deep learning training run fails or produces poor results, the Model Selection Agent must apply these recovery strategies before escalating to the Debug Agent:

Out-of-memory: halve the batch size. If still out of memory, enable gradient checkpointing. If still out of memory, switch to CPU with a warning logged.

Loss is NaN: verify that the input data contains no NaN or Inf values, reduce the learning rate by a factor of 10, add gradient clipping, and retry.

Loss does not decrease after five epochs: apply learning rate warmup (linear warmup over 10% of total steps), check weight initialisation (use PyTorch defaults unless a specific initialisation is required by the architecture), reduce model depth by one layer and retry.

Validation loss diverges from training loss (overfitting): increase dropout rate by 0.1, add L2 weight decay, apply stronger data augmentation, enable early stopping with a shorter patience.

Training accuracy is near chance level (underfitting): increase model capacity (add a layer or increase hidden dimensions), reduce regularisation, train for more epochs, verify that the labels are correct.

DataLoader crashes or hangs: reduce `num_workers` to 0 and retry. If that fixes it, increase `num_workers` one at a time to find the stable maximum.

---

## 12. Phase 1 — Foundation and Scaffolding

### Goal

At the end of this phase, you have a running skeleton: the project structure exists, both MCP servers are running and responding to requests, a single hello-world agent calls an LLM and logs to the Tracking MCP Server, the middleware chain fires on that call, and the Docker sandbox executes a trivial script.

### Steps

**Step 1.1 — Create the project repository**

Initialise a Git repository. Create a `.gitignore` that excludes `.env`, `__pycache__`, `.venv`, `*.pyc`, and any file larger than 10 MB. Create a `pyproject.toml` that pins all dependencies to exact versions. Do not use floating version ranges in production.

**Step 1.2 — Install the Microsoft Agent Framework**

Install `agent-framework` via pip. Verify the installation by running the minimal quickstart from the official documentation: a single agent that calls an LLM and prints the response. Do not proceed until this works.

**Step 1.3 — Provision Azure resources**

In the Azure portal or via Terraform (preferred), provision: one Azure OpenAI resource (or Azure Foundry project), one Azure Blob Storage account, one Azure ML Workspace, one Azure Cosmos DB account, one Azure Cognitive Search service, one Application Insights resource. All resources in the same region. Document every resource name, endpoint, and connection string in a `.env.example` file (without actual secrets).

**Step 1.4 — Implement the Tracking MCP Server**

Write a FastAPI application that implements the MCP tool endpoints listed in Section 4.1. Use Cosmos DB as the persistence layer. Test each endpoint individually with `curl`. Verify that `HEAD /` returns 200, `GET /` returns 405 with `Allow: POST`, and `POST /` with a well-formed MCP initialisation payload returns an `Mcp-Session-Id` header.

**Step 1.5 — Implement the DS Tools MCP Server scaffold**

Write a FastAPI application with stub implementations of all tools listed in Section 4.2. Stubs return hardcoded success responses for now. Real implementations come in later phases. Verify that it satisfies the MCP compliance checklist in Section 4.3.

**Step 1.6 — Implement the middleware chain**

Implement all five middleware classes (Logging, Rate Limiting, Safety, Retry, Telemetry) as described in Section 6. Register them on a test agent in the correct order. Write unit tests that verify each middleware fires correctly: logging middleware produces a JSON log entry, rate limiting pauses on limit hit, safety middleware raises an exception on a blocked pattern, retry middleware retries exactly N times on a transient error, telemetry middleware creates an OpenTelemetry span.

**Step 1.7 — Implement the hooks registry**

Implement the hooks registry as described in Section 7. Register all hooks. Write unit tests that verify each hook fires at the correct lifecycle event.

**Step 1.8 — Build the Docker sandbox image**

Write a `Dockerfile.sandbox` that installs all required libraries. Build it. Verify that the image can execute a trivial Python script (print statement only). Verify that the image has no outbound network access by attempting a `requests.get` inside the sandbox and confirming it raises a `ConnectionError`.

**Step 1.9 — Implement the Code Execution system**

Implement the `CodeSandbox` class that submits code to the Docker sandbox, captures stdout and stderr, collects output artifacts from `/workspace/output`, and returns a result object. Write integration tests that verify: a successful script returns its stdout, a script that raises an exception returns the traceback in stderr, a script that times out returns a timeout error, output files written to `/workspace/output` are collected and returned.

**Step 1.10 — Connect and smoke test**

Create a minimal Orchestrator agent connected to both MCP servers with the full middleware chain and hook registry. Send it a message. Verify that the Tracking MCP Server records the call, the middleware chain fires, the telemetry span appears in Application Insights, and the agent returns a coherent response.

### Phase 1 Exit Criteria

- Both MCP servers are running, healthy, and MCP-compliant
- A hello-world agent call logs to the Tracking MCP Server, fires all middleware, and creates a trace in Application Insights
- The Docker sandbox executes code and returns results correctly
- All unit tests and integration tests pass in CI

---

## 13. Phase 2 — Data Pipeline Agents

### Goal

At the end of this phase, the first four agents (Ingestion, EDA, Cleaning, Feature Engineering) run end-to-end on a sample dataset, producing real artifacts in Azure Blob Storage, with all events logged to the Tracking MCP Server and all middleware/hooks firing correctly.

### Steps

**Step 2.1 — Implement real tool backends**

Replace the stub implementations in the DS Tools MCP Server with real implementations for: `read_csv`, `read_blob`, `write_blob`, `query_sql`, `plot_chart`, and `run_code` (the sandbox integration). Each tool must be individually tested with a real data file.

**Step 2.2 — Implement the Data Ingestion Agent**

Write the Ingestion Agent's system prompt following the responsibilities in Section 3.2. Register the tools it needs (`read_csv`, `query_sql`, `read_blob`, `write_blob`). Register the `before_ingest` (validate URI accessible) and `after_ingest` (record snapshot URI to Tracking MCP) hooks. Test against: a local CSV file, a PostgreSQL connection, and an Azure Data Lake path. Each test must produce a snapshot in Blob Storage.

**Step 2.3 — Implement the EDA Agent**

Write the EDA Agent's system prompt. Implement the EDA code template that the agent generates (the template lives in the `templates/` directory, not inside the agent). The agent's job is to fill in the template with dataset-specific parameters and submit it to the sandbox. Implement the `plot_chart` tool backend (renders matplotlib figures and saves to Blob Storage). Test with the Titanic dataset. The output must include: a full statistics JSON, histogram URIs, a correlation heatmap URI, and a natural-language narrative.

**Step 2.4 — Integrate the Auto-Fix Loop into EDA**

Intentionally break the EDA code template (introduce a missing import). Verify that the auto-fix loop fires, the Debug Agent identifies the fix, the repaired code runs successfully, and all five attempts are logged to the Tracking MCP Server.

**Step 2.5 — Implement the Data Cleaning Agent**

Write the Cleaning Agent's system prompt with the chain-of-thought steps from Section 3.4. Implement the human-in-the-loop gate for outlier handling decisions. Implement the versioned storage pattern for cleaned datasets. Test with the Titanic dataset (which has known missing values and outliers). The output must include a versioned cleaned dataset and a transformation log.

**Step 2.6 — Implement the Feature Engineering Agent**

Write the Feature Engineering Agent's system prompt. Implement the DuckDuckGo research step first (it must fire before any feature creation). Implement each transform type. Implement the quick RandomForest importance run. Produce the `feature_manifest` artifact. Test with the House Prices dataset. The manifest must document every original column, every new feature, and every importance score.

**Step 2.7 — Wire agents into the Workflow Graph**

Connect Ingestion → EDA → Cleaning → Feature Engineering as a workflow with checkpoint gates between each stage. Run the full pipeline end-to-end on the Titanic dataset. Verify that the Tracking MCP Server contains records for all four stages, that all artifacts are in Blob Storage, and that a crash mid-run resumes from the last checkpoint.

### Phase 2 Exit Criteria

- Full data pipeline (Ingestion through Feature Engineering) runs end-to-end on Titanic and House Prices datasets
- All artifacts are in Blob Storage with versioned paths
- The auto-fix loop successfully repairs at least one injected error
- DuckDuckGo research fires and its results are logged
- The human-in-the-loop gate for outlier decisions works correctly
- All events are in the Tracking MCP Server

---

## 14. Phase 3 — Model Training and Tuning Agents

### Goal

At the end of this phase, the Model Selection, Training, and Hyperparameter Tuning agents run and produce real trained models logged to Azure ML Experiment Tracker, including at least one deep learning scenario.

### Steps

**Step 3.1 — Implement the train_sklearn and train_pytorch tool backends**

Both tools must submit code to the sandbox, capture the trained model artifact, log metrics, and return the artifact URI. The `train_sklearn` tool must support all algorithm types listed in Section 3.6. The `train_pytorch` tool must support the training loop requirements listed in Section 11.2.

**Step 3.2 — Implement the task type detector**

Write a utility that takes the target column, the data sample, and the user's task description and returns one of the scenario types listed in Section 11.1. Test with five different datasets that each map to a different scenario type.

**Step 3.3 — Implement the Model Selection Agent**

Write the system prompt. The agent must: run the task type detector, select appropriate algorithms, generate training code using the appropriate template from `templates/`, submit it to the sandbox via the `run_code` tool, capture metrics from the sandbox output, and log results to the Tracking MCP Server. Test on the Titanic dataset (classification) and the House Prices dataset (regression).

**Step 3.4 — Add DL scenario coverage**

Implement the DL training templates (one file per scenario type in `templates/dl/`). Test at minimum: text classification with BERT fine-tuning using the IMDB dataset, image classification with a CNN using CIFAR-10, and time series forecasting with an LSTM using the Air Passengers dataset. Each must satisfy every item in the training loop checklist from Section 11.2. Each must trigger at least one auto-remediation from the list in Section 11.3.

**Step 3.5 — Implement the Hyperparameter Tuning Agent**

Write the system prompt. The agent must: receive the best model from the Model Selection Agent, define a search space appropriate to that model type, submit an Optuna study to the sandbox, capture the best parameters and the full results, and produce the `best_params` and `tuning_report` artifacts. Test on the Titanic dataset. The best parameters must outperform the default parameters.

**Step 3.6 — Implement the log_experiment tool backend**

Connect to Azure ML Experiment Tracker and MLflow. Every training and tuning run must appear as a logged experiment with parameters, metrics, and artifact tags.

**Step 3.7 — Add deep learning auto-remediation**

Inject each failure mode listed in Section 11.3 into a test training run and verify that the correct recovery strategy is applied automatically. Document which recovery was applied in the Tracking MCP Server.

### Phase 3 Exit Criteria

- Classical ML pipeline produces a trained, logged model for both classification and regression tasks
- BERT fine-tuning on IMDB runs end-to-end in the sandbox
- CNN on CIFAR-10 runs end-to-end in the sandbox
- LSTM on Air Passengers runs end-to-end in the sandbox
- Hyperparameter tuning improves on default parameters
- All runs are visible in Azure ML Experiment Tracker

---

## 15. Phase 4 — Explainability, Reporting, and Deployment

### Goal

At the end of this phase, the full pipeline from data ingestion through model deployment runs end-to-end and produces a deployed endpoint with a monitoring configuration.

### Steps

**Step 4.1 — Implement the run_shap tool backend**

Connect SHAP to the sandbox. The tool must select the correct SHAP explainer based on the model type, compute global and local SHAP values, render the standard SHAP plots (beeswarm, bar, waterfall, force), save plots to Blob Storage, and return URIs. Test with the Titanic XGBoost model.

**Step 4.2 — Implement the Explainability Agent**

Write the system prompt. The agent must: receive the model artifact URI and the cleaned dataset URI, invoke `run_shap`, invoke LIME via `run_code`, invoke Captum for PyTorch models, collect all plot URIs, and generate the plain-English explanation. Test with the Titanic model (tree-based) and the BERT model (deep learning).

Add the Browser-Use error recovery: intentionally use an incorrect SHAP API call and verify that Browser-Use crawls the SHAP documentation and provides the correct usage.

**Step 4.3 — Implement the Evaluation and Validation Agent**

Write the system prompt with automatic metric selection. Implement the Fairlearn integration. Implement the KS test for data drift. Test on the Titanic dataset with age and gender as protected attributes. The fairness analysis must flag any violation.

**Step 4.4 — Implement the Report and Dashboard Agent**

Write the system prompt. Implement the Markdown and HTML report renderers. The HTML renderer must inline chart images as base64 so the report is self-contained. Implement the Power BI push as an optional, configuration-gated feature. Test with a complete Titanic pipeline run. The report must contain all sections listed in Section 3.10.

**Step 4.5 — Implement the deploy_endpoint tool backend**

Implement model serialisation (pickle, ONNX, TorchScript). Implement the FastAPI wrapper template. Implement the Dockerfile generation. Implement the Azure Container Instance deployment via the Azure SDK. Test the full deploy flow with the Titanic XGBoost model.

**Step 4.6 — Implement the Deployment and Monitoring Agent**

Write the system prompt. Connect the `before_deploy` hook (require evaluation report). Connect the `after_deploy` hook (run smoke test). Implement the Azure Monitor alert configuration. Test the full deploy flow. Verify that the smoke test passes and alerts are visible in the Azure portal.

### Phase 4 Exit Criteria

- SHAP plots are generated for the Titanic model with correct values
- Fairness analysis runs and correctly identifies a violation when one exists
- HTML report is self-contained and renders all sections
- Titanic model is deployed to Azure Container Instance and passes the smoke test
- Azure Monitor alerts are configured and visible

---

## 16. Phase 5 — Memory, Knowledge, and Retrospection

### Goal

At the end of this phase, the Memory Agent indexes all artifacts after every pipeline run, and natural-language queries against the index return correct, grounded answers.

### Steps

**Step 5.1 — Design the Cognitive Search index schema**

Define the index fields: `run_id`, `stage_name`, `artifact_type`, `artifact_uri`, `dataset_name`, `task_type`, `model_type`, `metric_name`, `metric_value`, `feature_count`, `timestamp`, `tags`. Enable semantic ranking on the `artifact_type` and `tags` fields.

**Step 5.2 — Implement the Memory Agent**

Write the event subscriber that listens to the Tracking MCP Server's `record_artifact` events. After each event, the Memory Agent must: extract the artifact metadata, construct the Cognitive Search document, and index it. This must happen asynchronously so it does not add latency to the pipeline.

**Step 5.3 — Implement the Cosmos DB lineage graph**

Design the graph schema: nodes are artifacts (model, dataset, feature manifest, report), edges are `derived_from` relationships. After each pipeline stage, the Memory Agent must add the new artifact node and connect it to its upstream artifact nodes.

**Step 5.4 — Implement the RAG query interface**

Write the query endpoint that: embeds the natural-language query using Azure OpenAI embeddings, queries the Cognitive Search index with semantic ranking, retrieves the top five documents, and passes them to Azure OpenAI to synthesise a grounded answer that cites the specific artifact URIs.

**Step 5.5 — Test retrospective queries**

Run three pipeline runs with different datasets and model types. Then verify that the following queries return correct, grounded answers: "What was the best ROC-AUC we achieved on a binary classification task?", "Which feature manifests were produced in the last 30 days?", "Show me all models trained with LightGBM."

### Phase 5 Exit Criteria

- Cognitive Search index is populated after every pipeline run
- Lineage graph in Cosmos DB correctly represents artifact dependencies
- All three retrospective test queries return correct answers

---

## 17. Phase 6 — Observability, Safety, and Hardening

### Goal

At the end of this phase, the full middleware chain is hardened, all hooks pass integration tests, telemetry traces are visible in Application Insights, and all safety guardrails are verified.

### Steps

**Step 6.1 — Harden the Safety Middleware**

Expand the blocked pattern list. Write a penetration test suite that attempts 20 different injection patterns (shell injection, SQL injection, path traversal, environment variable access, outbound HTTP from the sandbox). All 20 must be blocked.

**Step 6.2 — Add PII detection to the Ingestion Agent**

Integrate Microsoft Presidio into the `before_ingest` hook. Detect any PII columns (names, email addresses, phone numbers, national ID numbers) and mask them before the snapshot is written to Blob Storage. Log the masking decisions.

**Step 6.3 — Harden the Retry Middleware**

Write a suite of fault injection tests: simulate HTTP 429, 502, 503, 504, and timeouts. Verify that each is retried with exponential backoff. Simulate HTTP 400 and 401. Verify that these are not retried. Verify that the total wait time never exceeds the configured maximum.

**Step 6.4 — Complete the OpenTelemetry integration**

Verify that a full pipeline run produces a single distributed trace in Application Insights that shows all agent invocations, all MCP tool calls, and all sandbox executions as nested spans. Verify that the trace is complete — no spans are missing.

**Step 6.5 — Implement the token budget guardrail**

Add a per-run token budget to the configuration. The Telemetry Middleware must track cumulative token usage across all agents in a run. When the budget is 80% consumed, log a warning to the Tracking MCP Server. When the budget is 100% consumed, the Orchestrator must trigger a human-in-the-loop gate before proceeding.

**Step 6.6 — Conduct a full MCP compliance audit**

Run the MCP compliance checklist from Section 4.3 against both MCP servers. Run a suite of 50 MCP tool call integration tests covering: normal tool calls, malformed inputs, tool calls that exceed rate limits, tool calls that return errors, and concurrent tool calls.

### Phase 6 Exit Criteria

- All 20 injection penetration tests are blocked
- PII detection masks correctly in Ingestion Agent
- All retry fault injection tests pass
- Full pipeline trace is visible in Application Insights
- Token budget guardrail fires at 80% and 100%
- All 50 MCP tool call integration tests pass

---

## 18. Phase 7 — End-to-End Validation and Production Readiness

### Goal

At the end of this phase, the system runs five benchmark datasets end-to-end without human intervention, all production readiness criteria are met, and documentation is complete.

### Steps

**Step 7.1 — Run benchmark dataset 1: Titanic (binary classification)**

The pipeline must run from ingestion through deployment without any human intervention (remove all optional human-in-the-loop gates for this test). Inject one sandbox error at the EDA stage and verify the auto-fix loop repairs it. Verify that the deployed endpoint passes the smoke test.

**Step 7.2 — Run benchmark dataset 2: California Housing (regression)**

Verify that the task type detector correctly identifies this as a regression task. Verify that regression-appropriate metrics appear in the evaluation report. Verify the SHAP values are computed and rendered correctly for a regression model.

**Step 7.3 — Run benchmark dataset 3: Credit Card Fraud (imbalanced classification)**

Verify that class imbalance is detected and flagged in the EDA report. Verify that the Model Selection Agent uses class weighting or oversampling. Verify that the evaluation report includes PR-AUC (not just ROC-AUC, which is misleading for imbalanced data). Verify that Fairlearn analysis runs.

**Step 7.4 — Run benchmark dataset 4: IMDB Sentiment (BERT fine-tuning)**

Verify that the DL scenario detector identifies this as a text classification task. Verify that the BERT fine-tuning template is used. Verify that the training loop checklist from Section 11.2 is fully satisfied. Inject an out-of-memory error and verify the batch size halving remediation fires. The fine-tuned model must achieve above 90% validation accuracy.

**Step 7.5 — Run benchmark dataset 5: Air Passengers (time series with LSTM)**

Verify that the DL scenario detector identifies this as a time series forecasting task. Verify that the LSTM template is used. Verify that time-series-appropriate metrics (MASE, SMAPE) appear in the evaluation report. Verify that the model is deployed and the endpoint accepts a sequence input and returns a forecast.

**Step 7.6 — Performance benchmarks**

Run each benchmark dataset and record total wall-clock time. The targets are: tabular datasets (Titanic, California Housing, Credit Card Fraud) must complete in under 30 minutes each, IMDB must complete in under 2 hours with GPU, Air Passengers must complete in under 1 hour with GPU.

**Step 7.7 — Security review**

Conduct a security review covering: sandbox escape (verify no code can write outside `/workspace`), MCP server authentication (add API key authentication to both servers), Blob Storage access control (verify no public access), and secrets management (verify no secrets are logged or written to artifacts).

**Step 7.8 — Write documentation**

Write a README that covers: system architecture overview, prerequisites and installation, configuration reference, how to run a pipeline, how to query the Memory Agent, how to add a new agent, and how to extend the tool registry. Write an architecture diagram as a Mermaid diagram embedded in the README.

### Phase 7 Exit Criteria

- All five benchmark datasets complete end-to-end without human intervention
- All performance benchmarks are met
- Security review passes with no high-severity findings
- README is complete and accurate
- All tests pass in CI including the full end-to-end test suite

---

## 19. Directory and File Structure

Organise the project exactly as follows. Do not add top-level directories not listed here without updating this document first.

```
ds-agent/
├── agents/
│   ├── orchestrator.py
│   ├── ingestion.py
│   ├── eda.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── model_selection.py
│   ├── hp_tuning.py
│   ├── evaluation.py
│   ├── explainability.py
│   ├── reporting.py
│   ├── deployment.py
│   ├── monitoring.py
│   ├── memory.py
│   └── debug.py
├── middleware/
│   ├── __init__.py
│   ├── chain.py              — assembles and orders the middleware stack
│   ├── logging_mw.py
│   ├── rate_limit_mw.py
│   ├── safety_mw.py
│   ├── retry_mw.py
│   └── telemetry_mw.py
├── hooks/
│   ├── __init__.py
│   └── registry.py           — all hooks defined and registered here
├── mcp_servers/
│   ├── tracking/
│   │   ├── server.py         — FastAPI app, port 8100
│   │   ├── tools.py          — tool implementations
│   │   └── persistence.py    — Cosmos DB layer
│   └── ds_tools/
│       ├── server.py         — FastAPI app, port 8101
│       ├── tools.py          — tool implementations
│       └── registry.py       — tool registry
├── tools/
│   ├── code_execution.py
│   ├── sql_query.py
│   ├── azure_blob.py
│   ├── azure_ml.py
│   ├── plot_chart.py
│   ├── shap_tool.py
│   ├── browser_use_tool.py
│   ├── duckduckgo_tool.py
│   └── deploy_tool.py
├── sandbox/
│   ├── executor.py
│   ├── Dockerfile.sandbox
│   └── requirements.sandbox.txt
├── templates/
│   ├── eda_template.py
│   ├── cleaning_template.py
│   ├── feature_template.py
│   ├── sklearn_train_template.py
│   ├── eval_template.py
│   └── dl/
│       ├── bert_text_classification.py
│       ├── cnn_image_classification.py
│       ├── lstm_time_series.py
│       ├── rag_system.py
│       ├── llm_finetune.py
│       ├── object_detection.py
│       └── tabular_deep.py
├── workflows/
│   ├── pipeline_graph.py     — full workflow graph definition
│   └── checkpointing.py      — checkpoint read and write logic
├── memory/
│   ├── indexer.py            — Cognitive Search indexing
│   ├── lineage.py            — Cosmos DB graph
│   └── rag_query.py          — RAG query interface
├── config/
│   ├── settings.py           — Pydantic settings model
│   ├── .env.example          — template without secrets
│   └── safety_patterns.py    — blocked pattern list
├── docs/
│   ├── error_catalogue.md    — known errors and fix strategies
│   ├── doc_site_registry.md  — library name → documentation URL mapping
│   └── decision_log.md       — architecture decisions
├── tests/
│   ├── unit/
│   │   ├── test_middleware.py
│   │   ├── test_hooks.py
│   │   ├── test_sandbox.py
│   │   └── test_mcp_compliance.py
│   ├── integration/
│   │   ├── test_ingestion_agent.py
│   │   ├── test_eda_agent.py
│   │   ├── test_auto_fix_loop.py
│   │   └── test_mcp_tool_calls.py
│   └── e2e/
│       ├── test_titanic_pipeline.py
│       ├── test_housing_pipeline.py
│       ├── test_fraud_pipeline.py
│       ├── test_imdb_pipeline.py
│       └── test_air_passengers_pipeline.py
├── main.py                   — CLI entry point
├── pyproject.toml
├── README.md
└── .github/
    └── workflows/
        └── ci.yml            — lint, type-check, unit tests, integration tests
>>>>>>> origin/main
```

---

<<<<<<< HEAD
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
=======
## 20. Configuration Reference

All configuration lives in environment variables. The settings module reads them via a Pydantic BaseSettings model. Document every setting below. The `.env.example` file must contain all keys with placeholder values and a comment explaining each.

**Azure Settings**

- `AZURE_FOUNDRY_ENDPOINT` — the Azure Foundry project endpoint URL
- `AZURE_FOUNDRY_PROJECT` — the Azure Foundry project name
- `AZURE_OPENAI_ENDPOINT` — Azure OpenAI endpoint (if not using Foundry)
- `AZURE_OPENAI_API_KEY` — Azure OpenAI API key (stored in Key Vault in production; never in `.env` in production)
- `AZURE_BLOB_ACCOUNT_NAME` — Azure Blob Storage account name
- `AZURE_BLOB_CONTAINER_NAME` — container name for all pipeline artifacts
- `AZURE_ML_SUBSCRIPTION_ID` — Azure ML workspace subscription ID
- `AZURE_ML_RESOURCE_GROUP` — Azure ML workspace resource group
- `AZURE_ML_WORKSPACE_NAME` — Azure ML workspace name
- `AZURE_COGNITIVE_SEARCH_ENDPOINT` — Azure Cognitive Search endpoint
- `AZURE_COGNITIVE_SEARCH_KEY` — Azure Cognitive Search admin key
- `COSMOS_DB_ENDPOINT` — Cosmos DB endpoint
- `COSMOS_DB_KEY` — Cosmos DB primary key
- `APPINSIGHTS_CONNECTION_STRING` — Application Insights connection string

**Agent Framework Settings**

- `DEFAULT_MODEL` — default model name (e.g., `gpt-5.4-mini`)
- `ORCHESTRATOR_MODEL` — model for the Orchestrator (can be larger/more capable)
- `DEBUG_AGENT_MODEL` — model for the Debug Agent
- `DEFAULT_MAX_TOKENS` — default max tokens per completion (1024 recommended)
- `DEFAULT_TEMPERATURE` — default temperature (0.1 for reasoning and code agents)

**MCP Settings**

- `TRACKING_MCP_URL` — full URL of the Tracking MCP Server
- `DS_TOOLS_MCP_URL` — full URL of the DS Tools MCP Server
- `MCP_API_KEY` — shared secret for MCP server authentication

**Sandbox Settings**

- `SANDBOX_DOCKER_IMAGE` — Docker image name and tag for the sandbox
- `SANDBOX_TIMEOUT_SECONDS` — wall-clock timeout for sandbox execution (default 300)
- `SANDBOX_MEMORY_LIMIT` — memory limit string for Docker (default `4g`)
- `SANDBOX_CPU_LIMIT` — CPU limit as a float number of cores (default 2.0)
- `MAX_AUTO_FIX_ATTEMPTS` — maximum repair attempts before escalation (default 5)

**Research Tool Settings**

- `BROWSER_USE_API_KEY` — Browser-Use cloud API key (for production cloud mode)
- `BROWSER_USE_CLOUD_PROFILE_ID` — Browser-Use cloud browser profile ID
- `BROWSER_USE_HEADLESS` — boolean, default true
- `BROWSER_USE_MAX_STEPS` — maximum navigation steps per Browser-Use run (default 50)
- `DUCKDUCKGO_MAX_RESULTS` — maximum results per DuckDuckGo query (default 10)
- `DUCKDUCKGO_RATE_LIMIT_PER_HOUR` — maximum DuckDuckGo searches per hour (default 30)

**Pipeline Settings**

- `ENABLE_AUTOML` — boolean, whether to submit Azure AutoML runs (default false)
- `AUTOML_TIMEOUT_MINUTES` — timeout for AutoML runs (default 60)
- `ENABLE_POWER_BI` — boolean, whether to push reports to Power BI (default false)
- `TOKEN_BUDGET_PER_RUN` — maximum tokens per pipeline run before escalation
- `ENABLE_HUMAN_IN_THE_LOOP` — boolean, whether to pause for human decisions (default true)
- `CHECKPOINT_ENABLED` — boolean, whether to checkpoint after each stage (default true)

---

## 21. Security and Responsible AI Checklist

Complete every item on this checklist before declaring any phase complete.

**Data Security**

- All data in transit uses TLS 1.2 or higher
- All data at rest in Blob Storage uses Azure Storage Service Encryption
- PII detection and masking runs in the Ingestion Agent before any snapshot is written
- The sandbox has no outbound network access
- No secrets appear in logs, artifacts, or MCP tool call records

**Access Control**

- Both MCP servers require API key authentication on every request
- Azure resources use managed identity (not API keys) wherever possible
- The sandbox Docker image runs as a non-root user
- Blob Storage has no public access enabled

**Responsible AI**

- Fairness analysis (Fairlearn) runs on every classification model before deployment
- The `before_deploy` hook blocks deployment if a fairness violation is not acknowledged
- Every model artifact includes a model card documenting: training data description, known limitations, intended use cases, and prohibited use cases
- SHAP explanations are produced for every deployed model
- Data drift monitoring is configured for every deployed endpoint

**Operational Security**

- All middleware and hook exceptions are caught and logged without exposing internal stack traces in MCP responses
- The maximum retry count is hard-coded and cannot be overridden by agent-generated inputs
- The blocked pattern list in the Safety Middleware is reviewed and updated before each production release
- All Azure resource access uses the principle of least privilege

---

## 22. Verification Checklist per Phase

Use this table to track completion. Mark each row only after the exit criteria in the corresponding phase section are fully met.

| Phase | Name | Exit Criteria Verified | Date |
|---|---|---|---|
| 1 | Foundation and Scaffolding | | |
| 2 | Data Pipeline Agents | | |
| 3 | Model Training and Tuning | | |
| 4 | Explainability, Reporting, Deployment | | |
| 5 | Memory and Knowledge | | |
| 6 | Observability and Hardening | | |
| 7 | End-to-End Validation | | |

---

## Reference Documents

The following external documents are the authoritative sources for the technologies referenced in this specification. When this document conflicts with these sources, the external sources take precedence (update this document accordingly).

- Microsoft Agent Framework documentation: `learn.microsoft.com/en-us/agent-framework/overview`
- Microsoft Agent Framework GitHub: `github.com/microsoft/agent-framework`
- MCP Protocol Specification 2025-06-18: `modelcontextprotocol.io/specification`
- Claude Managed Agents documentation: `platform.claude.com/docs/en/managed-agents/overview`
- Browser-Use documentation: `docs.browser-use.com`
- Browser-Use full LLM reference: `docs.browser-use.com/llms-full.txt`
- Azure ML SDK v2 documentation: `learn.microsoft.com/en-us/azure/machine-learning/`
- Azure Cognitive Search documentation: `learn.microsoft.com/en-us/azure/search/`
- Fairlearn documentation: `fairlearn.org/main/user_guide/index.html`
- SHAP documentation: `shap.readthedocs.io`
- Optuna documentation: `optuna.readthedocs.io`

---

*This document is the primary implementation reference for the Data Science Agent project. All architectural decisions must be recorded in `docs/decision_log.md`. All changes to this document require a pull request with at least one reviewer.*
>>>>>>> origin/main
