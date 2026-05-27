"""
Data Ingestion Agent - Loads data from various sources and provides schema information.
"""

import pandas as pd
from typing import Optional
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..storage import get_storage_client
from ..registry import get_registry


class DataSchema(BaseModel):
    """Schema information for a dataset."""
    columns: list[dict]  # [{name, dtype, missing_count, missing_pct, unique_count}]
    total_rows: int
    total_columns: int
    memory_usage_mb: float


class IngestionResult(BaseModel):
    """Result from data ingestion."""
    dataset_id: str
    success: bool
    data_schema: Optional[DataSchema] = None
    error: Optional[str] = None
    sample_data: Optional[list[dict]] = None  # First few rows as dicts


class IngestionAgent(BaseAgent):
    """
    Agent responsible for loading data from various sources.
    
    Supports:
    - Local CSV, Parquet, JSON, Excel files
    - Remote URLs
    - Registered datasets from datasets.yaml
    """
    
    def __init__(self):
        super().__init__("Ingestion Agent")
        self.storage = get_storage_client()
        self.registry = get_registry()
        self._current_df: Optional[pd.DataFrame] = None
    
    def run(self, dataset_id: str, **kwargs) -> IngestionResult:
        """
        Load a dataset and extract schema information.
        
        Args:
            dataset_id: Name of registered dataset or path to file
            
        Returns:
            IngestionResult with schema and sample data
        """
        self.log(f"Loading dataset: {dataset_id}")
        
        try:
            # Load the data
            df = self.storage.load_dataframe(dataset_id)
            self._current_df = df
            
            # Extract schema
            schema = self._extract_schema(df)
            
            # Get sample data (first 5 rows)
            sample = df.head(5).to_dict(orient="records")
            
            # Store in memory
            summary = self._create_summary(dataset_id, schema)
            self.store_result(
                category="ingestion_summary",
                content=summary,
                dataset_id=dataset_id,
                metadata={
                    "rows": schema.total_rows,
                    "columns": schema.total_columns,
                    "memory_mb": schema.memory_usage_mb
                }
            )
            
            self.log(f"✓ Loaded {schema.total_rows} rows, {schema.total_columns} columns")
            
            return IngestionResult(
                dataset_id=dataset_id,
                success=True,
                data_schema=schema,
                sample_data=sample
            )
            
        except Exception as e:
            self.log(f"✗ Failed to load dataset: {e}")
            return IngestionResult(
                dataset_id=dataset_id,
                success=False,
                error=str(e)
            )
    
    def _extract_schema(self, df: pd.DataFrame) -> DataSchema:
        """Extract schema information from DataFrame."""
        columns = []
        
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "missing_count": int(df[col].isna().sum()),
                "missing_pct": round(df[col].isna().mean() * 100, 2),
                "unique_count": int(df[col].nunique())
            }
            columns.append(col_info)
        
        return DataSchema(
            columns=columns,
            total_rows=len(df),
            total_columns=len(df.columns),
            memory_usage_mb=round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        )
    
    def _create_summary(self, dataset_id: str, schema: DataSchema) -> str:
        """Create a text summary of the ingested data."""
        missing_cols = [
            c["name"] for c in schema.columns 
            if c["missing_pct"] > 0
        ]
        
        summary = f"""Dataset '{dataset_id}' loaded successfully.
- Total rows: {schema.total_rows:,}
- Total columns: {schema.total_columns}
- Memory usage: {schema.memory_usage_mb:.2f} MB
"""
        
        if missing_cols:
            summary += f"- Columns with missing values: {', '.join(missing_cols[:5])}"
            if len(missing_cols) > 5:
                summary += f" (+{len(missing_cols) - 5} more)"
        else:
            summary += "- No missing values detected"
        
        return summary
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the currently loaded DataFrame."""
        return self._current_df


if __name__ == "__main__":
    # Test the ingestion agent
    agent = IngestionAgent()
    
    # Test with a registered dataset
    from ..registry import get_registry
    registry = get_registry()
    datasets = registry.list_datasets()
    
    if datasets:
        result = agent.run(datasets[0])
        print(f"\nResult: {result.success}")
        if result.data_schema:
            print(f"Schema: {result.data_schema.total_rows} rows, "
                  f"{result.data_schema.total_columns} cols")
    else:
        print("No datasets registered. Add entries to datasets.yaml")
