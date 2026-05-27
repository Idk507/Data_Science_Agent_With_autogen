"""
EDA Agent - Performs exploratory data analysis and generates insights using Azure OpenAI.
"""

import pandas as pd
import numpy as np
from typing import Optional
from pydantic import BaseModel

from .base_agent import BaseAgent


class ColumnStats(BaseModel):
    """Statistics for a single column."""
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    # Numeric columns
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    median: Optional[float] = None
    # Categorical columns
    top_values: Optional[list[dict]] = None  # [{value, count, pct}]
    # Warnings
    warnings: list[str] = []


class EDAResult(BaseModel):
    """Result from EDA analysis."""
    dataset_id: str
    success: bool
    summary_stats: Optional[dict] = None
    column_stats: list[ColumnStats] = []
    warnings: list[str] = []
    correlations: Optional[dict] = None  # Top correlations
    llm_insights: Optional[str] = None  # AI-generated insights
    error: Optional[str] = None


class EDAAgent(BaseAgent):
    """
    Agent responsible for exploratory data analysis.
    
    Performs:
    - Summary statistics computation
    - Missing value analysis
    - Outlier detection
    - Correlation analysis
    - AI-generated insights via Azure OpenAI
    """
    
    def __init__(self):
        super().__init__("EDA Agent")
    
    def run(self, df: pd.DataFrame, dataset_id: str, **kwargs) -> EDAResult:
        """
        Perform EDA on the provided DataFrame.
        
        Args:
            df: pandas DataFrame to analyze
            dataset_id: Identifier for the dataset
            
        Returns:
            EDAResult with statistics and insights
        """
        self.log(f"Analyzing dataset: {dataset_id}")
        
        try:
            # Get context from previous runs
            context = self.get_context(dataset_id)
            
            # Compute statistics
            column_stats = self._compute_column_stats(df)
            summary_stats = self._compute_summary_stats(df)
            correlations = self._compute_correlations(df)
            
            # Collect warnings
            warnings = self._collect_warnings(column_stats, df)
            
            # Generate AI insights
            llm_insights = self._generate_insights(
                df, column_stats, summary_stats, correlations, warnings, context
            )
            
            # Store results in memory
            self._store_eda_results(
                dataset_id, summary_stats, column_stats, warnings, llm_insights
            )
            
            self.log(f"✓ Analysis complete. Found {len(warnings)} warnings.")
            
            return EDAResult(
                dataset_id=dataset_id,
                success=True,
                summary_stats=summary_stats,
                column_stats=column_stats,
                warnings=warnings,
                correlations=correlations,
                llm_insights=llm_insights
            )
            
        except Exception as e:
            self.log(f"✗ EDA failed: {e}")
            return EDAResult(
                dataset_id=dataset_id,
                success=False,
                error=str(e)
            )
    
    def _compute_column_stats(self, df: pd.DataFrame) -> list[ColumnStats]:
        """Compute statistics for each column."""
        stats = []
        
        for col in df.columns:
            col_data = df[col]
            warnings = []
            
            base_stats = {
                "name": col,
                "dtype": str(col_data.dtype),
                "missing_count": int(col_data.isna().sum()),
                "missing_pct": round(col_data.isna().mean() * 100, 2),
                "unique_count": int(col_data.nunique())
            }
            
            # Check for high missing rate
            if base_stats["missing_pct"] > 30:
                warnings.append(f"High missing rate: {base_stats['missing_pct']:.1f}%")
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                clean_data = col_data.dropna()
                if len(clean_data) > 0:
                    base_stats["mean"] = round(float(clean_data.mean()), 4)
                    base_stats["std"] = round(float(clean_data.std()), 4)
                    base_stats["min"] = round(float(clean_data.min()), 4)
                    base_stats["max"] = round(float(clean_data.max()), 4)
                    base_stats["median"] = round(float(clean_data.median()), 4)
                    
                    # Check for outliers using IQR
                    q1, q3 = clean_data.quantile([0.25, 0.75])
                    iqr = q3 - q1
                    outlier_count = ((clean_data < q1 - 1.5 * iqr) | 
                                     (clean_data > q3 + 1.5 * iqr)).sum()
                    if outlier_count > len(clean_data) * 0.05:
                        warnings.append(f"Contains {outlier_count} potential outliers")
            
            # Categorical/Object columns
            elif pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
                value_counts = col_data.value_counts().head(5)
                top_values = [
                    {
                        "value": str(v),
                        "count": int(c),
                        "pct": round(c / len(df) * 100, 2)
                    }
                    for v, c in value_counts.items()
                ]
                base_stats["top_values"] = top_values
                
                # Check for high cardinality
                if base_stats["unique_count"] > len(df) * 0.5:
                    warnings.append("High cardinality - may need encoding")
            
            base_stats["warnings"] = warnings
            stats.append(ColumnStats(**base_stats))
        
        return stats
    
    def _compute_summary_stats(self, df: pd.DataFrame) -> dict:
        """Compute overall summary statistics."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "total_missing": int(df.isna().sum().sum()),
            "missing_pct": round(df.isna().sum().sum() / (len(df) * len(df.columns)) * 100, 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
    
    def _compute_correlations(self, df: pd.DataFrame) -> dict:
        """Compute correlations for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"message": "Not enough numeric columns for correlation"}
        
        try:
            corr_matrix = numeric_df.corr()
            
            # Get top correlations (excluding self-correlations)
            correlations = []
            for i, col1 in enumerate(corr_matrix.columns):
                for col2 in corr_matrix.columns[i+1:]:
                    corr_val = corr_matrix.loc[col1, col2]
                    if not pd.isna(corr_val):
                        correlations.append({
                            "col1": col1,
                            "col2": col2,
                            "correlation": round(float(corr_val), 4)
                        })
            
            # Sort by absolute correlation
            correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            return {
                "top_positive": [c for c in correlations if c["correlation"] > 0.5][:5],
                "top_negative": [c for c in correlations if c["correlation"] < -0.5][:5],
                "all_correlations": correlations[:20]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _collect_warnings(self, column_stats: list[ColumnStats], 
                          df: pd.DataFrame) -> list[str]:
        """Collect all warnings from the analysis."""
        warnings = []
        
        # Column-level warnings
        for col in column_stats:
            for w in col.warnings:
                warnings.append(f"Column '{col.name}': {w}")
        
        # Dataset-level warnings
        if df.duplicated().sum() > 0:
            dup_pct = df.duplicated().mean() * 100
            warnings.append(f"Dataset contains {df.duplicated().sum()} duplicate rows ({dup_pct:.1f}%)")
        
        total_missing = df.isna().sum().sum()
        if total_missing > 0:
            missing_pct = total_missing / (len(df) * len(df.columns)) * 100
            warnings.append(f"Dataset has {total_missing} missing values ({missing_pct:.1f}% of all cells)")
        
        return warnings
    
    def _generate_insights(self, df: pd.DataFrame, 
                           column_stats: list[ColumnStats],
                           summary_stats: dict,
                           correlations: dict,
                           warnings: list[str],
                           context: str) -> str:
        """Generate AI-powered insights using Azure OpenAI."""
        
        # Create a compact summary for the LLM
        columns_summary = []
        for col in column_stats[:10]:  # Limit to first 10 columns
            col_info = f"- {col.name} ({col.dtype}): {col.missing_pct}% missing"
            if col.mean is not None:
                col_info += f", mean={col.mean:.2f}, std={col.std:.2f}"
            if col.top_values:
                top = col.top_values[0]
                col_info += f", top value='{top['value']}' ({top['pct']:.1f}%)"
            columns_summary.append(col_info)
        
        # Format correlations
        corr_text = ""
        if isinstance(correlations, dict):
            top_pos = correlations.get("top_positive", [])
            top_neg = correlations.get("top_negative", [])
            if top_pos:
                corr_text += "Strong positive correlations:\n"
                for c in top_pos[:3]:
                    corr_text += f"  - {c['col1']} & {c['col2']}: {c['correlation']:.2f}\n"
            if top_neg:
                corr_text += "Strong negative correlations:\n"
                for c in top_neg[:3]:
                    corr_text += f"  - {c['col1']} & {c['col2']}: {c['correlation']:.2f}\n"
        
        prompt = f"""Analyze this dataset and provide key insights:

## Dataset Summary
- Rows: {summary_stats['total_rows']:,}
- Columns: {summary_stats['total_columns']} ({summary_stats['numeric_columns']} numeric, {summary_stats['categorical_columns']} categorical)
- Missing values: {summary_stats['missing_pct']:.1f}%
- Duplicate rows: {summary_stats['duplicate_rows']}

## Column Details
{chr(10).join(columns_summary)}

## Correlations
{corr_text if corr_text else "No strong correlations found."}

## Warnings
{chr(10).join(warnings[:10]) if warnings else "No significant warnings."}

## Previous Context
{context if context != "No previous context available." else "This is the first analysis of this dataset."}

Please provide:
1. A brief overview of the dataset (2-3 sentences)
2. Key observations about data quality
3. Notable patterns or relationships
4. Recommendations for data cleaning or feature engineering
5. Any potential issues to be aware of

Keep the response concise and actionable (under 400 words)."""

        system_prompt = """You are a data science expert analyzing datasets. 
Provide clear, actionable insights. Be specific and reference actual column names and statistics.
Focus on practical recommendations for the next steps in the data science pipeline."""

        try:
            insights = self.call_llm(prompt, system_prompt, max_tokens=800, temperature=0.3)
            return insights
        except Exception as e:
            self.log(f"Warning: LLM insights generation failed: {e}")
            return f"LLM insights unavailable: {e}"
    
    def _store_eda_results(self, dataset_id: str, 
                           summary_stats: dict,
                           column_stats: list[ColumnStats],
                           warnings: list[str],
                           llm_insights: str) -> None:
        """Store EDA results in memory."""
        # Store summary
        summary_text = f"""EDA Summary for {dataset_id}:
- {summary_stats['total_rows']:,} rows, {summary_stats['total_columns']} columns
- Missing: {summary_stats['missing_pct']:.1f}%
- Duplicates: {summary_stats['duplicate_rows']}
- Warnings: {len(warnings)}"""
        
        self.store_result(
            category="eda_summary",
            content=summary_text,
            dataset_id=dataset_id,
            metadata=summary_stats
        )
        
        # Store warnings separately
        if warnings:
            self.store_result(
                category="data_warnings",
                content="\n".join(warnings),
                dataset_id=dataset_id,
                metadata={"warning_count": len(warnings)}
            )
        
        # Store LLM insights
        if llm_insights and not llm_insights.startswith("LLM insights unavailable"):
            self.store_result(
                category="llm_insights",
                content=llm_insights,
                dataset_id=dataset_id
            )


if __name__ == "__main__":
    # Test the EDA agent
    import pandas as pd
    
    # Create sample data
    np.random.seed(42)
    df = pd.DataFrame({
        "id": range(100),
        "age": np.random.randint(18, 80, 100),
        "income": np.random.normal(50000, 15000, 100),
        "category": np.random.choice(["A", "B", "C"], 100),
        "score": np.random.uniform(0, 100, 100)
    })
    df.loc[5:10, "income"] = np.nan  # Add some missing values
    
    agent = EDAAgent()
    result = agent.run(df, "test_dataset")
    
    print(f"\nSuccess: {result.success}")
    print(f"Warnings: {len(result.warnings)}")
    if result.llm_insights:
        print(f"\nLLM Insights:\n{result.llm_insights[:500]}...")
