## AutoDS Implementation Plan

### Phase 0 – Setup & Orchestrator Skeleton
1. Create basic project layout: `autods/` package, `autods_cli.py`, `config.py`, `agents/`.
2. Add config handling: `.env` + `config.py` exposing Azure keys/connection strings and local paths.
3. Implement a minimal **Orchestrator Agent** (no real logic yet) that:
   - Accepts a `dataset_id` and `goal` (e.g., “EDA report”).
   - Calls stub methods `run_ingestion()`, `run_eda()`, `run_reporting()`.
   - Logs each step and returns a simple “workflow completed” message.
4. Add an Azure OpenAI client wrapper (even if not heavily used yet) wired from `config.py`.
5. Verify you can run: `python autods_cli.py --dataset demo_sales --goal eda_report` and see the stubs executed.

### Phase 1 – Data Ingestion Agent (Local + Azure Blob)
1. Create a simple `datasets.yaml` with entries like:
   - `demo_sales: local:./data/demo_sales.csv`
   - (Later) `big_sales_2024: blob:container/path/big_sales_2024.csv`.
2. Implement a small **Dataset Registry** module that:
   - Loads `datasets.yaml`.
   - Resolves `dataset_id` → `{uri, format, source_type}`.
3. Implement a **Storage Client** that:
   - If `uri` starts with `local:`, uses `pandas.read_csv`.
   - If `uri` starts with `blob:`, uses `azure-storage-blob` to download and then `pandas.read_csv`.
4. Implement the **Data Ingestion Agent** that:
   - Input: `dataset_id`.
   - Uses registry + storage client to return a pandas DataFrame and simple schema (`column`, `dtype`, `missing_ratio`).
5. Wire the orchestrator so `run_ingestion()` calls the Data Ingestion Agent and passes its DataFrame to the EDA stub.
6. Test locally on a small CSV under `data/`.

### Phase 2 – EDA Agent + Text-Only Reporting (MVP Pipeline)
1. Implement **EDA Agent**:
   - Input: DataFrame (and optional schema from ingestion).
   - Compute: `df.describe()`, value counts for categoricals, missingness summary, basic outlier detection (e.g., z-score on numeric).
   - Assemble a structured dict: summary stats, per-column info, top warnings (e.g., “column A has 30% nulls”).
2. Integrate Azure OpenAI in EDA Agent:
   - Prompt LLM with a compact summary (not full data) to generate 1–2 paragraph natural-language EDA commentary.
   - Add the text commentary to the EDA result dict.
3. Implement **Reporting Agent v1 (Markdown)**:
   - Input: EDA result dict (stats + commentary).
   - Use a simple template to create a Markdown report: introduction, dataset overview, column summaries, LLM commentary.
   - Save report under `reports/{dataset_id}_{timestamp}.md` and return its path.
4. Update Orchestrator:
   - `run_ingestion()` → DataFrame.
   - `run_eda()` → EDA result.
   - `run_reporting()` → report path.
   - Orchestrator returns a small response object: `{"dataset_id": ..., "report_path": ...}`.
5. Extend CLI: `autods run --dataset demo_sales` should:
   - Run the full chain.
   - Print the report path at the end.
6. Test with 1–2 small CSVs; verify the whole Ingestion → EDA → Reporting loop works locally.

### Phase 3 – Azure Hardening (Configs, AML/Storage Awareness)
1. Clean up config:
   - Add `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_STORAGE_ACCOUNT`, `AZURE_BLOB_CONTAINER`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_ML_WORKSPACE_NAME`.
   - Use `DefaultAzureCredential` if possible, fall back to API keys in `.env` for dev.
2. Refine Storage Client:
   - Use a single abstraction like `load_table(uri) -> DataFrame` that supports `local:`, `blob:`, and later `abfss:`/`azureml://` URIs.
3. Add a small **Azure ML Connector** (not full pipelines yet):
   - Create and bind an `MLClient`.
   - Implement helper functions: `register_data_asset(name, local_path_or_uri)`, `list_data_assets()`.
4. Extend Dataset Registry:
   - Allow entries that point to Azure ML data assets or Data Lake URIs.
   - On resolution, either return a direct path if local/Blob, or use AML/Data Lake APIs to get a real file path/URI and pass it to the Storage Client.
5. Optional: Add a flag at CLI level (`--register-data`) so that after EDA, cleaned dataset or profile can be registered as an Azure ML data asset (stub for later phases).

### Phase 4 – Data Cleaning & Feature Engineering Agents
1. Implement **Data Cleaning Agent**:
   - Input: raw DataFrame + EDA summary.
   - Decide on simple deterministic rules: drop columns with >X% missing, fill numeric nulls with median, categoricals with mode.
   - Use Azure OpenAI only to generate explanation text; do not let it execute arbitrary code.
   - Output: cleaned DataFrame + transformation log (list of steps applied).
2. Update Orchestrator to support:
   - A mode with or without cleaning (`--with-cleaning` CLI flag).
   - If enabled: Ingestion → Cleaning → EDA → Reporting.
3. Implement **Feature Engineering Agent**:
   - Input: cleaned DataFrame + simple config (type of problem, e.g., regression/classification).
   - Deterministically create new features: date parts (year, month, weekday), ratios, log transforms, label encoding for small categoricals.
   - Output: feature-enhanced DataFrame + feature definitions (metadata).
4. Let Orchestrator optionally insert Feature Engineering between Cleaning and EDA (or between EDA and Modeling once modeling is added).
5. Use Azure ML Connector to register raw, cleaned, and feature-engineered datasets as versioned data assets for later modeling.

### Phase 5 – Modeling, Evaluation & Rich Reporting
1. Implement **Model Selection & Training Agent**:
   - Input: dataset asset or DataFrame + target column + problem type.
   - For MVP, run a small set of scikit-learn models locally (e.g., LogisticRegression, RandomForest, XGBoost) with train/test split.
   - Log metrics (accuracy, F1, RMSE, etc.) in a simple local store; optionally sync to Azure ML.
2. Evolve to Azure ML jobs:
   - Wrap the modeling logic into an Azure ML job (script or AutoML run) via `azure-ai-ml`.
   - The agent submits the job, polls for completion, and retrieves metrics + model path.
3. Implement **Evaluation & Validation Agent**:
   - Compute additional metrics (ROC, PR, confusion matrix) on holdout data.
   - Summarize key performance findings in plain language (using Azure OpenAI for narration).
4. Implement **Explainability Agent**:
   - Use SHAP or LIME on the trained model and a sample of data.
   - Generate per-feature importance plots and save them to disk or Blob.
   - Use Azure OpenAI to summarize “top drivers” in text.
5. Upgrade **Reporting Agent to v2**:
   - Include model performance section, key metrics tables.
   - Embed or link plots (EDA visuals, SHAP plots).
   - Optionally prepare an export format that’s easy to plug into Power BI (CSV of metrics, feature importances).

### Phase 6 – Deployment, Monitoring & Memory/Knowledge
1. Implement **Deployment & Monitoring Agent**:
   - Given a selected model, create a simple scoring service (start as a local FastAPI/Flask; later Azure Functions or ACI).
   - Package model and dependencies; deploy via Azure ML managed endpoint or Azure Functions.
   - Return endpoint URL and a sample test payload.
2. Implement **Monitoring Hooks**:
   - Capture predictions + inputs in a log store (blob or table).
   - Later: integrate with Azure Monitor/Application Insights for latency, error rate, and drift metrics.
3. Implement **Memory & Knowledge Agent**:
   - Store references to datasets (raw/clean/feature), models (versions, metrics), and reports and explainability artifacts.
   - Back this with a simple metadata store first (JSON or small DB), then integrate Azure Cognitive Search for semantic queries.
4. Expose a simple conversational front-end later:
   - A “Chat” agent that translates user questions into queries against the Memory & Knowledge store and routes to Explainability or Reporting when needed.
