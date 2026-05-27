"""
Autogen Configuration for Azure OpenAI (v0.4+ API).

This module provides the model client and code execution settings
for the new Autogen multi-agent framework.
"""

import os
from pathlib import Path
from typing import Optional, Any

from ..config import get_config


def get_azure_model_client() -> Any:
    """
    Get Azure OpenAI model client for Autogen v0.4+.
    
    Returns:
        AzureOpenAIChatCompletionClient: Model client for agents
    """
    try:
        from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    except ImportError:
        raise ImportError(
            "autogen_ext not installed. Run: pip install autogen-ext[openai]"
        )
    
    config = get_config()
    azure_cfg = config.azure_openai
    
    if not azure_cfg.is_configured:
        raise ValueError(
            "Azure OpenAI is not configured. Please check your .env file."
        )
    
    # Create Azure OpenAI client for Autogen v0.4+
    client = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_cfg.deployment_name,
        model=azure_cfg.deployment_name,
        api_version=azure_cfg.api_version,
        azure_endpoint=azure_cfg.endpoint,
        api_key=azure_cfg.api_key,
    )
    
    return client


def get_code_execution_work_dir(dataset_id: Optional[str] = None) -> Path:
    """
    Get working directory for code execution.
    
    Args:
        dataset_id: Optional dataset identifier
    
    Returns:
        Path to working directory
    """
    config = get_config()
    
    if dataset_id:
        work_dir = config.paths.artifacts_dir / f"ml_{dataset_id}"
    else:
        work_dir = config.paths.artifacts_dir / "ml_workspace"
    
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


# Legacy config for backward compatibility
def get_autogen_llm_config() -> dict:
    """
    Legacy LLM config (for reference only).
    Use get_azure_model_client() instead for v0.4+.
    """
    config = get_config()
    azure_cfg = config.azure_openai
    
    return {
        "azure_deployment": azure_cfg.deployment_name,
        "api_version": azure_cfg.api_version,
        "azure_endpoint": azure_cfg.endpoint,
        "api_key": azure_cfg.api_key,
    }


def get_code_execution_config(work_dir: Optional[Path] = None) -> dict:
    """Legacy code execution config."""
    if work_dir is None:
        work_dir = get_code_execution_work_dir()
    
    return {
        "work_dir": str(work_dir),
        "use_docker": False,
        "timeout": 300,
    }


if __name__ == "__main__":
    # Test configuration
    print("=== Autogen Configuration Test (v0.4+) ===")
    
    try:
        client = get_azure_model_client()
        print(f"✓ Azure OpenAI client created")
        print(f"  Type: {type(client).__name__}")
        
        work_dir = get_code_execution_work_dir("test")
        print(f"\n✓ Work directory: {work_dir}")
        
    except Exception as e:
        print(f"\n✗ Configuration error: {e}")
