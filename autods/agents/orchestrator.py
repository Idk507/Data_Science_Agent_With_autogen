"""
Orchestrator - Central coordinator that sequences and manages all agents.
"""

import pandas as pd
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from .base_agent import BaseAgent
from .ingestion_agent import IngestionAgent, IngestionResult
from .eda_agent import EDAAgent, EDAResult
from .reporting_agent import ReportingAgent, ReportResult
from ..config import get_config
from ..memory import get_memory


class WorkflowStage(str, Enum):
    """Stages in the data science workflow."""
    INGESTION = "ingestion"
    EDA = "eda"
    CLEANING = "cleaning"
    FEATURE_ENGINEERING = "feature_engineering"
    MODELING = "modeling"
    EVALUATION = "evaluation"
    REPORTING = "reporting"


class WorkflowResult(BaseModel):
    """Result from a complete workflow run."""
    dataset_id: str
    goal: str
    success: bool
    stages_completed: list[str] = []
    stages_failed: list[str] = []
    ingestion_result: Optional[IngestionResult] = None
    eda_result: Optional[EDAResult] = None
    report_result: Optional[ReportResult] = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True


class Orchestrator(BaseAgent):
    """
    Central orchestrator that coordinates all agents.
    
    Responsibilities:
    - Sequence agent execution based on workflow goals
    - Pass data and artifacts between agents
    - Handle errors and recovery
    - Log execution progress
    - Store workflow state in memory
    """
    
    def __init__(self):
        super().__init__("Orchestrator")
        self.config = get_config()
        
        # Initialize agents
        self.ingestion_agent = IngestionAgent()
        self.eda_agent = EDAAgent()
        self.reporting_agent = ReportingAgent()
        
        # Current workflow state
        self._current_df: Optional[pd.DataFrame] = None
        self._current_dataset_id: Optional[str] = None
    
    def run(self, dataset_id: str, goal: str = "eda_report", **kwargs) -> WorkflowResult:
        """
        Execute a complete workflow.
        
        Args:
            dataset_id: Name of dataset to process
            goal: Workflow goal:
                - "eda_report": Run ingestion → EDA → reporting
                - "full_pipeline": Run all stages (future)
            **kwargs: Additional options
                - with_cleaning: bool - Include cleaning stage
                - report_format: str - "markdown" or "html"
            
        Returns:
            WorkflowResult with all stage results
        """
        start_time = datetime.now()
        
        self.log(f"Starting workflow: goal='{goal}', dataset='{dataset_id}'")
        self.log("=" * 60)
        
        result = WorkflowResult(
            dataset_id=dataset_id,
            goal=goal,
            success=False
        )
        
        try:
            # Initialize config
            self.config.initialize()
            
            # Execute workflow based on goal
            if goal == "eda_report":
                result = self._run_eda_workflow(dataset_id, result, **kwargs)
            elif goal == "full_pipeline":
                # Future: full ML pipeline
                result = self._run_eda_workflow(dataset_id, result, **kwargs)
            else:
                result.error = f"Unknown goal: {goal}"
                return result
            
        except Exception as e:
            self.log(f"✗ Workflow failed with error: {e}")
            result.error = str(e)
        
        # Calculate execution time
        result.execution_time_seconds = (datetime.now() - start_time).total_seconds()
        
        # Log summary
        self.log("=" * 60)
        if result.success:
            self.log(f"✓ Workflow completed successfully in {result.execution_time_seconds:.2f}s")
            self.log(f"  Stages completed: {', '.join(result.stages_completed)}")
            if result.report_result and result.report_result.report_path:
                self.log(f"  Report: {result.report_result.report_path}")
        else:
            self.log(f"✗ Workflow failed: {result.error}")
            if result.stages_failed:
                self.log(f"  Failed stages: {', '.join(result.stages_failed)}")
        
        # Store workflow result in memory
        self._store_workflow_result(result)
        
        return result
    
    def _run_eda_workflow(self, dataset_id: str, 
                          result: WorkflowResult,
                          **kwargs) -> WorkflowResult:
        """Run the EDA workflow: Ingestion → EDA → Reporting."""
        
        # Stage 1: Data Ingestion
        self.log("\n📥 Stage 1: Data Ingestion")
        self.log("-" * 40)
        
        ingestion_result = self.ingestion_agent.run(dataset_id)
        result.ingestion_result = ingestion_result
        
        if not ingestion_result.success:
            result.stages_failed.append("ingestion")
            result.error = f"Ingestion failed: {ingestion_result.error}"
            return result
        
        result.stages_completed.append("ingestion")
        self._current_df = self.ingestion_agent.get_dataframe()
        self._current_dataset_id = dataset_id
        
        # Stage 2: EDA
        self.log("\n📊 Stage 2: Exploratory Data Analysis")
        self.log("-" * 40)
        
        if self._current_df is None:
            result.stages_failed.append("eda")
            result.error = "No DataFrame available for EDA"
            return result
        
        eda_result = self.eda_agent.run(self._current_df, dataset_id)
        result.eda_result = eda_result
        
        if not eda_result.success:
            result.stages_failed.append("eda")
            result.error = f"EDA failed: {eda_result.error}"
            return result
        
        result.stages_completed.append("eda")
        
        # Stage 3: Reporting
        self.log("\n📝 Stage 3: Report Generation")
        self.log("-" * 40)
        
        report_format = kwargs.get("report_format", "markdown")
        report_result = self.reporting_agent.run(
            eda_result, 
            report_format=report_format
        )
        result.report_result = report_result
        
        if not report_result.success:
            result.stages_failed.append("reporting")
            result.error = f"Reporting failed: {report_result.error}"
            return result
        
        result.stages_completed.append("reporting")
        result.success = True
        
        return result
    
    def _store_workflow_result(self, result: WorkflowResult) -> None:
        """Store workflow result in memory."""
        status = "success" if result.success else "failed"
        summary = f"""Workflow {status}: {result.goal}
Dataset: {result.dataset_id}
Completed: {', '.join(result.stages_completed)}
Time: {result.execution_time_seconds:.2f}s"""
        
        if result.error:
            summary += f"\nError: {result.error}"
        
        self.store_result(
            category="workflow_result",
            content=summary,
            dataset_id=result.dataset_id,
            metadata={
                "goal": result.goal,
                "success": result.success,
                "stages_completed": result.stages_completed,
                "execution_time": result.execution_time_seconds
            }
        )
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the current working DataFrame."""
        return self._current_df


def run_workflow(dataset_id: str, goal: str = "eda_report", **kwargs) -> WorkflowResult:
    """
    Convenience function to run a workflow.
    
    Args:
        dataset_id: Name of dataset to process
        goal: Workflow goal
        **kwargs: Additional options
        
    Returns:
        WorkflowResult
    """
    orchestrator = Orchestrator()
    return orchestrator.run(dataset_id, goal, **kwargs)


if __name__ == "__main__":
    # Test the orchestrator
    from ..registry import get_registry
    
    registry = get_registry()
    datasets = registry.list_datasets()
    
    if datasets:
        result = run_workflow(datasets[0], "eda_report")
        print(f"\n\nFinal Result:")
        print(f"  Success: {result.success}")
        print(f"  Stages: {result.stages_completed}")
        if result.report_result:
            print(f"  Report: {result.report_result.report_path}")
    else:
        print("No datasets registered. Add entries to datasets.yaml")
