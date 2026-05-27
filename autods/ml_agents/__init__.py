"""
AutoDS ML Agents Package - Autogen-based multi-agent ML pipeline.

This package implements a multi-agent system using the Autogen framework
for automated machine learning including:
- Data preprocessing
- Model selection and training
- Hyperparameter tuning
- Model evaluation
- Result interpretation
"""

from .autogen_config import get_azure_model_client, get_code_execution_work_dir
from .ml_orchestrator import MLOrchestrator
from .agents import (
    create_data_scientist_agent,
    create_model_builder_agent,
    create_hyperparameter_tuner_agent,
    create_evaluator_agent,
)

__all__ = [
    "get_azure_model_client",
    "get_code_execution_work_dir",
    "MLOrchestrator",
    "create_data_scientist_agent",
    "create_model_builder_agent",
    "create_hyperparameter_tuner_agent",
    "create_evaluator_agent",
]
