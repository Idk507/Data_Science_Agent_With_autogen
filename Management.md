
---

## 🚀 Step 0: Project Kickoff & Setup  
1. **Create your repo & board**  
   - Fork `AI_Agents_Hackathon` and create a feature branch (`feature/multi‑agent‑ds`).  
   - Stand up a lightweight Kanban board (GitHub Projects, Trello) with columns: Backlog, In Progress, Review, Done.  
2. **Define global contracts & orchestrator stub**  
   - Draft a JSON schema for agent calls:  
     ```json
     { "agent": "string", "inputs": {…}, "outputs": {…}, "status": "pending|done|error" }
     ```  
   - Build an empty **Orchestrator Agent** skeleton (just log and forward calls).  
3. **Environment**  
   - Spin up a Python 3.10 venv, install Autogen + Azure AI SDKs.  
   - Verify you can run `az login` and call a test OpenAI prompt.

---

## 🗄️ Step 1: Data Ingestion Agent  
1. **Define Interface**  
   - Inputs: connection string / file path  
   - Outputs: raw DataFrame location (Blob URI)  
2. **Implement MVP**  
   - Use pandas / Azure Data Factory SDK to fetch and save a CSV to Blob.  
   - Return a JSON with `{"blob_uri": "...", "row_count": 1234}`.  
3. **Unit Test**  
   - Mock a small CSV, assert blob upload and correct row count.  
4. **Integrate**  
   - Wire into Orchestrator: call ingestion, receive blob URI, pass to next agent.

---

## 📊 Step 2: Data Profiling Agent  
1. **Define Interface**  
   - Inputs: `blob_uri`  
   - Outputs: profiling report JSON (column stats) + sample CSV.  
2. **Implement MVP**  
   - Use `pandas_profiling.ProfileReport` or Azure ML DataPrep to generate summary.  
   - Serialize key stats (null %, dtypes, unique counts).  
3. **Test & Validate**  
   - Run on a known dataset; compare output to hand‑computed stats.  
4. **Integration**  
   - Hook profiling agent after ingestion; store its JSON in orchestrator’s state.

---

## 📈 Step 3: EDA & Visualization Agent  
1. **Define Interface**  
   - Inputs: profiling JSON + sample data  
   - Outputs: list of chart specs + generated PNG URLs + text insights.  
2. **Implement Chart Recommendation**  
   - Prompt GPT‑4 (Autogen) with schema → suggest `["histogram", "heatmap", …]`.  
3. **Static Plot Agent**  
   - In a sandbox, execute matplotlib code to render each chart, upload to Blob, return URLs.  
4. **Insight Extraction**  
   - Prompt GPT‑4 with chart stats → generate short narrative (“Sales peaked in Q4…”).  
5. **Test**  
   - Validate on a small dataset; ensure charts look correct and insights make sense.  
6. **Integrate**  
   - Connect to orchestrator; show sample chart + insight in logs/UI.

---

## 🧹 Step 4: Data Cleaning Agent  
1. **Define Interface**  
   - Inputs: raw blob URI, profiling JSON  
   - Outputs: cleaned data blob URI + log of actions taken.  
2. **Implement MVP**  
   - Auto‑impute numeric nulls (median), drop constant columns.  
   - Use Autogen prompts to suggest alternative strategies.  
3. **Test**  
   - Feed in synthetic data with known nulls/outliers; confirm cleaning.  
4. **Integrate**  
   - Place after EDA; pass cleaned data URI downstream.

---

## ⚙️ Step 5: Feature Engineering Agent  
1. **Define Interface**  
   - Inputs: cleaned data URI  
   - Outputs: features dataset URI + feature metadata JSON  
2. **Implement**  
   - One‑hot encode categoricals, scale numerics, generate date‑based features.  
   - Optionally embed text columns with Azure ML embeddings API.  
3. **Test**  
   - Run on toy data, inspect output shape and metadata.  
4. **Integrate**  
   - Update orchestrator to route cleaned data into this agent.

---

## 🤖 Step 6: Model Training Agent  
1. **Define Interface**  
   - Inputs: features URI + target column  
   - Outputs: model artifact URI + baseline metrics  
2. **Implement MVP**  
   - Train a simple scikit‑learn model (e.g., RandomForest) in an Azure ML Pipeline.  
   - Log to Azure ML Experiment.  
3. **Test**  
   - Ensure model serializes, metrics match expected.  
4. **Integrate**  
   - Connect training agent; pass its artifact URI to the tuning agent.

---

## 🔍 Step 7: Hyperparameter Tuning Agent  
1. **Define Interface**  
   - Inputs: model artifact + parameter grid  
   - Outputs: best model URI + best params  
2. **Implement**  
   - Use Azure ML HyperDrive or Optuna in parallel runs.  
3. **Test**  
   - On a small grid, confirm the best trial is selected.  
4. **Integrate**  
   - Chain after baseline training agent.

---

## 📏 Step 8: Evaluation & Validation Agent  
1. **Define Interface**  
   - Inputs: best model URI + test set URI  
   - Outputs: metrics JSON + confusion/ROC plot URLs  
2. **Implement**  
   - Compute metrics (AUC, RMSE, etc.), generate and upload plots.  
3. **Test**  
   - Validate metrics on known splits.  
4. **Integrate**  
   - Slot in after tuning agent.

---

## 🔍 Step 9: Explainability Agent  
1. **Define Interface**  
   - Inputs: model URI + sample data  
   - Outputs: SHAP/LIME plot URLs + narrative JSON  
2. **Implement**  
   - Compute SHAP values, render plots, prompt GPT‑4 for plain‑English.  
3. **Test**  
   - Verify plot correctness and summary clarity.  
4. **Integrate**  
   - Connect to orchestrator to enrich final report.

---

## 📑 Step 10: Reporting & Dashboard Agent  
1. **Define Interface**  
   - Inputs: all prior outputs (charts, metrics, explanations)  
   - Outputs: HTML/Markdown report URI + Power BI dashboard link  
2. **Implement**  
   - Use Jinja2 to stitch narrative + visuals into a report.  
   - Optionally publish to Power BI via REST API.  
3. **Test**  
   - Generate sample report, review formatting and links.  
4. **Integrate**  
   - Final step of orchestrator’s pipeline.

---

## 🚢 Step 11: Deployment & Monitoring Agent  
1. **Define Interface**  
   - Inputs: final model URI  
   - Outputs: endpoint URL + monitoring dashboard link  
2. **Implement**  
   - Containerize model as Azure Container Instance or Function.  
   - Hook up Application Insights for latency, error, drift alerts.  
3. **Test**  
   - Send test invokes, simulate drift, confirm alerts.  
4. **Integrate**  
   - Tie into orchestrator’s “go‑live” command.

---

## 🔄 Step 12: Feedback & Knowledge Agent  
1. **Define Interface**  
   - Inputs: user feedback events + artifact metadata  
   - Outputs: retraining triggers + Q&A endpoint  
2. **Implement**  
   - Store feedback in Cosmos DB.  
   - Use Azure Cognitive Search + GPT‑4 to answer “What was our last AUC?”  
3. **Test**  
   - Simulate feedback, query the knowledge agent.  
4. **Integrate**  
   - Hook into post‑deployment monitoring cycle.

---

## ✅ Step 13: End‑to‑End Integration & Release  
1. **Smoke Test**  
   - Run the full pipeline on a sample dataset.  
   - Fix any orchestration or data‑flow issues.  
2. **Documentation & Demo**  
   - Update `README.md` with setup, agent contracts, and usage.  
   - Capture a 2‑min demo GIF/video showing each agent’s output.  
3. **Submit**  
   - Fill out the `project.yml` in the hackathon repo, linking code, report, and demo.  
   - Review in “Review” column, then move to “Done.”

---
