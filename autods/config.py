"""
Configuration management for AutoDS.
Loads environment variables and provides typed config access.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration."""
    endpoint: str = Field(default_factory=lambda: os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT", "").strip().strip('"'))
    deployment_name: str = Field(default_factory=lambda: os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME", "gpt-4").strip().strip('"'))
    api_version: str = Field(default_factory=lambda: os.getenv("AI_FOUNDRY_API_VERSION", "2024-12-01-preview").strip().strip('"'))
    api_key: str = Field(default_factory=lambda: os.getenv("AI_FOUNDRY_API_KEY", "").strip().strip('"'))
    
    @property
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return bool(self.endpoint and self.api_key and self.deployment_name)


class PathsConfig(BaseModel):
    """File system paths configuration."""
    project_root: Path = Field(default=PROJECT_ROOT)
    data_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "data")
    reports_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "reports")
    artifacts_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "artifacts")
    vectorstore_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "vectorstore")
    memory_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "memory")
    datasets_file: Path = Field(default_factory=lambda: PROJECT_ROOT / "datasets.yaml")
    
    def ensure_dirs(self) -> None:
        """Create all necessary directories if they don't exist."""
        for dir_path in [self.data_dir, self.reports_dir, self.artifacts_dir, 
                         self.vectorstore_dir, self.memory_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


class AutoDSConfig(BaseModel):
    """Main configuration container."""
    azure_openai: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    
    def validate_config(self) -> list[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        if not self.azure_openai.is_configured:
            issues.append("Azure OpenAI is not properly configured. Check .env file.")
        
        if not self.paths.datasets_file.exists():
            issues.append(f"Datasets file not found: {self.paths.datasets_file}")
        
        return issues
    
    def initialize(self) -> None:
        """Initialize the configuration (create dirs, etc.)."""
        self.paths.ensure_dirs()


# Global config instance
config = AutoDSConfig()


def get_config() -> AutoDSConfig:
    """Get the global configuration instance."""
    return config


def get_openai_config() -> dict:
    """Get OpenAI configuration as a dictionary for Autogen."""
    cfg = config.azure_openai
    return {
        "model": cfg.deployment_name,
        "api_key": cfg.api_key,
        "base_url": f"{cfg.endpoint.rstrip('/')}/openai/deployments/{cfg.deployment_name}",
        "api_version": cfg.api_version,
        "api_type": "azure"
    }


if __name__ == "__main__":
    # Test configuration
    cfg = get_config()
    cfg.initialize()
    
    print("=== AutoDS Configuration ===")
    print(f"Project Root: {cfg.paths.project_root}")
    print(f"Azure OpenAI Configured: {cfg.azure_openai.is_configured}")
    print(f"Endpoint: {cfg.azure_openai.endpoint}")
    print(f"Deployment: {cfg.azure_openai.deployment_name}")
    
    issues = cfg.validate_config()
    if issues:
        print("\nConfiguration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ Configuration valid!")
