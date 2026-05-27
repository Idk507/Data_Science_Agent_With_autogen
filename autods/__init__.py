"""
AutoDS: A Multi-Agent Data Science & Analytics Platform
Built on Autogen + Azure OpenAI + ChromaDB

Key Components:
- EDA Pipeline: Automated exploratory data analysis with reporting
- ML Pipeline: Multi-agent ML training, tuning, and evaluation (Autogen)
- Memory System: ChromaDB-backed context and conversation memory
"""

__version__ = "0.2.0"
__author__ = "AutoDS Team"

# Core imports
from .config import get_config, get_openai_config
from .memory import get_memory
from .registry import get_registry
from .storage import get_storage_client


# Lazy imports for ML agents (requires autogen)
def get_ml_orchestrator():
    """Get the ML Orchestrator class (lazy import)."""
    from .ml_agents import MLOrchestrator
    return MLOrchestrator


__all__ = [
    "get_config",
    "get_openai_config",
    "get_memory",
    "get_registry",
    "get_storage_client",
    "get_ml_orchestrator",
]
