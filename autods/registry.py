"""
Dataset Registry - Maps dataset names to their locations and metadata.
Supports local files and URLs.
"""

import yaml
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from enum import Enum

from .config import get_config


class SourceType(str, Enum):
    """Type of data source."""
    LOCAL = "local"
    URL = "url"


class DatasetInfo(BaseModel):
    """Information about a registered dataset."""
    name: str
    uri: str
    source_type: SourceType
    format: str = "csv"  # csv, parquet, json
    description: Optional[str] = None
    
    @classmethod
    def from_uri_string(cls, name: str, uri_string: str) -> "DatasetInfo":
        """Parse a URI string like 'local:./data/file.csv' into DatasetInfo."""
        if uri_string.startswith("local:"):
            path = uri_string[6:]  # Remove 'local:' prefix
            source_type = SourceType.LOCAL
        elif uri_string.startswith("http://") or uri_string.startswith("https://"):
            path = uri_string
            source_type = SourceType.URL
        elif uri_string.startswith("url:"):
            path = uri_string[4:]  # Remove 'url:' prefix
            source_type = SourceType.URL
        else:
            # Assume local path if no prefix
            path = uri_string
            source_type = SourceType.LOCAL
        
        # Detect format from extension
        format_ext = Path(path).suffix.lower().lstrip(".")
        if format_ext in ["csv", "parquet", "json", "xlsx", "pkl"]:
            file_format = format_ext
        else:
            file_format = "csv"  # Default
        
        return cls(
            name=name,
            uri=path,
            source_type=source_type,
            format=file_format
        )


class DatasetRegistry:
    """Registry for managing dataset definitions."""
    
    def __init__(self, datasets_file: Optional[Path] = None):
        """Initialize the registry."""
        self.datasets_file = datasets_file or get_config().paths.datasets_file
        self._datasets: dict[str, DatasetInfo] = {}
        self._load_datasets()
    
    def _load_datasets(self) -> None:
        """Load datasets from YAML file."""
        if not self.datasets_file.exists():
            print(f"Warning: Datasets file not found: {self.datasets_file}")
            return
        
        try:
            with open(self.datasets_file, "r") as f:
                data = yaml.safe_load(f) or {}
            
            datasets_section = data.get("datasets", data)  # Support both formats
            
            for name, value in datasets_section.items():
                if isinstance(value, str):
                    # Simple format: name: uri
                    self._datasets[name] = DatasetInfo.from_uri_string(name, value)
                elif isinstance(value, dict):
                    # Extended format with metadata
                    uri = value.get("uri", value.get("path", ""))
                    info = DatasetInfo.from_uri_string(name, uri)
                    info.description = value.get("description")
                    if "format" in value:
                        info.format = value["format"]
                    self._datasets[name] = info
                    
        except Exception as e:
            print(f"Error loading datasets file: {e}")
    
    def get(self, name: str) -> Optional[DatasetInfo]:
        """Get dataset info by name."""
        return self._datasets.get(name)
    
    def list_datasets(self) -> list[str]:
        """List all registered dataset names."""
        return list(self._datasets.keys())
    
    def register(self, name: str, uri: str, description: Optional[str] = None) -> DatasetInfo:
        """Register a new dataset (in memory only)."""
        info = DatasetInfo.from_uri_string(name, uri)
        info.description = description
        self._datasets[name] = info
        return info
    
    def resolve_path(self, name: str) -> Optional[Path]:
        """Resolve a dataset name to its full local path (for local sources only)."""
        info = self.get(name)
        if not info or info.source_type != SourceType.LOCAL:
            return None
        
        path = Path(info.uri)
        if not path.is_absolute():
            path = get_config().paths.project_root / path
        
        return path


# Global registry instance
_registry: Optional[DatasetRegistry] = None


def get_registry() -> DatasetRegistry:
    """Get the global dataset registry instance."""
    global _registry
    if _registry is None:
        _registry = DatasetRegistry()
    return _registry


if __name__ == "__main__":
    # Test registry
    registry = get_registry()
    print("=== Dataset Registry ===")
    print(f"Registered datasets: {registry.list_datasets()}")
    
    for name in registry.list_datasets():
        info = registry.get(name)
        print(f"\n{name}:")
        print(f"  URI: {info.uri}")
        print(f"  Type: {info.source_type}")
        print(f"  Format: {info.format}")
