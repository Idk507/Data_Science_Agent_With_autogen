"""
Storage Client - Unified interface for loading data from local files and URLs.
"""

import pandas as pd
import requests
from pathlib import Path
from typing import Optional, Union
from io import StringIO, BytesIO

from .config import get_config
from .registry import DatasetInfo, SourceType, get_registry


class StorageClient:
    """Unified storage client for loading data from various sources."""
    
    def __init__(self):
        """Initialize the storage client."""
        self.config = get_config()
    
    def load_dataframe(self, source: Union[str, DatasetInfo, Path]) -> pd.DataFrame:
        """
        Load data into a pandas DataFrame.
        
        Args:
            source: Can be:
                - Dataset name (string) - looked up in registry
                - DatasetInfo object
                - Path to local file
                - URL string
        
        Returns:
            pandas DataFrame
        """
        # Resolve source to DatasetInfo
        if isinstance(source, str):
            # Check if it's a registered dataset name
            registry = get_registry()
            info = registry.get(source)
            
            if info:
                return self._load_from_info(info)
            
            # Check if it's a URL
            if source.startswith("http://") or source.startswith("https://"):
                return self._load_from_url(source)
            
            # Check if it's a local path
            path = Path(source)
            if not path.is_absolute():
                path = self.config.paths.project_root / source
            
            if path.exists():
                return self._load_from_local(path)
            
            raise ValueError(f"Could not resolve source: {source}")
        
        elif isinstance(source, DatasetInfo):
            return self._load_from_info(source)
        
        elif isinstance(source, Path):
            return self._load_from_local(source)
        
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")
    
    def _load_from_info(self, info: DatasetInfo) -> pd.DataFrame:
        """Load DataFrame from DatasetInfo."""
        if info.source_type == SourceType.LOCAL:
            path = Path(info.uri)
            if not path.is_absolute():
                path = self.config.paths.project_root / path
            return self._load_from_local(path, info.format)
        
        elif info.source_type == SourceType.URL:
            return self._load_from_url(info.uri, info.format)
        
        else:
            raise ValueError(f"Unsupported source type: {info.source_type}")
    
    def _load_from_local(self, path: Path, format: Optional[str] = None) -> pd.DataFrame:
        """Load DataFrame from local file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Detect format from extension if not provided
        if format is None:
            format = path.suffix.lower().lstrip(".")
        
        if format == "csv":
            return pd.read_csv(path)
        elif format == "parquet":
            return pd.read_parquet(path)
        elif format == "json":
            return pd.read_json(path)
        elif format == "xlsx" or format == "xls":
            return pd.read_excel(path)
        elif format == "pkl" or format == "pickle":
            return pd.read_pickle(path)
        else:
            # Try CSV as default
            return pd.read_csv(path)
    
    def _load_from_url(self, url: str, format: Optional[str] = None) -> pd.DataFrame:
        """Load DataFrame from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {url}. Error: {e}")
        
        # Detect format from URL if not provided
        if format is None:
            url_path = url.split("?")[0]  # Remove query params
            format = Path(url_path).suffix.lower().lstrip(".")
        
        content = response.content
        
        if format == "csv":
            return pd.read_csv(BytesIO(content))
        elif format == "parquet":
            return pd.read_parquet(BytesIO(content))
        elif format == "json":
            return pd.read_json(BytesIO(content))
        elif format == "xlsx" or format == "xls":
            return pd.read_excel(BytesIO(content))
        else:
            # Try CSV as default
            return pd.read_csv(BytesIO(content))
    
    def save_dataframe(self, df: pd.DataFrame, path: Union[str, Path], 
                       format: Optional[str] = None) -> Path:
        """
        Save DataFrame to a file.
        
        Args:
            df: DataFrame to save
            path: Output path (relative or absolute)
            format: File format (csv, parquet, pkl, json)
        
        Returns:
            Absolute path to saved file
        """
        path = Path(path)
        if not path.is_absolute():
            path = self.config.paths.artifacts_dir / path
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Detect format from extension if not provided
        if format is None:
            format = path.suffix.lower().lstrip(".")
        
        if format == "csv":
            df.to_csv(path, index=False)
        elif format == "parquet":
            df.to_parquet(path, index=False)
        elif format == "json":
            df.to_json(path, orient="records", indent=2)
        elif format == "pkl" or format == "pickle":
            df.to_pickle(path)
        else:
            # Default to CSV
            df.to_csv(path, index=False)
        
        return path


# Global client instance
_client: Optional[StorageClient] = None


def get_storage_client() -> StorageClient:
    """Get the global storage client instance."""
    global _client
    if _client is None:
        _client = StorageClient()
    return _client


if __name__ == "__main__":
    # Test storage client
    client = get_storage_client()
    print("=== Storage Client Test ===")
    
    # List available datasets
    from .registry import get_registry
    registry = get_registry()
    
    for name in registry.list_datasets():
        try:
            df = client.load_dataframe(name)
            print(f"\n{name}: Loaded successfully")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)[:5]}...")
        except Exception as e:
            print(f"\n{name}: Failed to load - {e}")
