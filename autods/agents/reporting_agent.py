"""
Reporting Agent - Generates Markdown/HTML reports from analysis results.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .base_agent import BaseAgent
from .eda_agent import EDAResult
from ..config import get_config


class ReportResult(BaseModel):
    """Result from report generation."""
    dataset_id: str
    success: bool
    report_path: Optional[str] = None
    report_format: str = "markdown"
    error: Optional[str] = None


class ReportingAgent(BaseAgent):
    """
    Agent responsible for generating reports.
    
    Generates:
    - Markdown reports for EDA results
    - Optional HTML export
    - Summary dashboards
    """
    
    def __init__(self):
        super().__init__("Reporting Agent")
        self.config = get_config()
    
    def run(self, eda_result: EDAResult, 
            report_format: str = "markdown",
            include_sample: bool = True,
            **kwargs) -> ReportResult:
        """
        Generate a report from EDA results.
        
        Args:
            eda_result: EDAResult from EDA Agent
            report_format: Output format ("markdown" or "html")
            include_sample: Whether to include sample data
            
        Returns:
            ReportResult with path to generated report
        """
        dataset_id = eda_result.dataset_id
        self.log(f"Generating report for: {dataset_id}")
        
        try:
            # Generate report content
            if report_format == "markdown":
                content = self._generate_markdown_report(eda_result, include_sample)
                extension = ".md"
            else:
                content = self._generate_html_report(eda_result, include_sample)
                extension = ".html"
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{dataset_id}_{timestamp}{extension}"
            report_path = self.config.paths.reports_dir / filename
            
            # Ensure directory exists
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Store in memory
            self.store_result(
                category="report_generated",
                content=f"Report generated: {filename}",
                dataset_id=dataset_id,
                metadata={
                    "path": str(report_path),
                    "format": report_format,
                    "timestamp": timestamp
                }
            )
            
            self.log(f"✓ Report saved to: {report_path}")
            
            return ReportResult(
                dataset_id=dataset_id,
                success=True,
                report_path=str(report_path),
                report_format=report_format
            )
            
        except Exception as e:
            self.log(f"✗ Report generation failed: {e}")
            return ReportResult(
                dataset_id=dataset_id,
                success=False,
                error=str(e)
            )
    
    def _generate_markdown_report(self, eda: EDAResult, 
                                   include_sample: bool = True) -> str:
        """Generate a Markdown report."""
        lines = []
        
        # Header
        lines.append(f"# EDA Report: {eda.dataset_id}")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary Statistics
        if eda.summary_stats:
            stats = eda.summary_stats
            lines.append("## Dataset Overview")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Rows | {stats.get('total_rows', 'N/A'):,} |")
            lines.append(f"| Total Columns | {stats.get('total_columns', 'N/A')} |")
            lines.append(f"| Numeric Columns | {stats.get('numeric_columns', 'N/A')} |")
            lines.append(f"| Categorical Columns | {stats.get('categorical_columns', 'N/A')} |")
            lines.append(f"| Missing Values (%) | {stats.get('missing_pct', 'N/A')}% |")
            lines.append(f"| Duplicate Rows | {stats.get('duplicate_rows', 'N/A')} |")
            lines.append(f"| Memory Usage | {stats.get('memory_mb', 'N/A')} MB |")
            lines.append("")
        
        # Warnings
        if eda.warnings:
            lines.append("## ⚠️ Data Quality Warnings")
            lines.append("")
            for warning in eda.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Column Details
        if eda.column_stats:
            lines.append("## Column Analysis")
            lines.append("")
            
            # Numeric columns
            numeric_cols = [c for c in eda.column_stats if c.mean is not None]
            if numeric_cols:
                lines.append("### Numeric Columns")
                lines.append("")
                lines.append("| Column | Type | Missing % | Mean | Std | Min | Max |")
                lines.append("|--------|------|-----------|------|-----|-----|-----|")
                for col in numeric_cols:
                    lines.append(
                        f"| {col.name} | {col.dtype} | {col.missing_pct}% | "
                        f"{col.mean:.2f} | {col.std:.2f} | {col.min:.2f} | {col.max:.2f} |"
                    )
                lines.append("")
            
            # Categorical columns
            cat_cols = [c for c in eda.column_stats if c.top_values]
            if cat_cols:
                lines.append("### Categorical Columns")
                lines.append("")
                lines.append("| Column | Type | Missing % | Unique | Top Value | Top Value % |")
                lines.append("|--------|------|-----------|--------|-----------|-------------|")
                for col in cat_cols:
                    top = col.top_values[0] if col.top_values else {"value": "N/A", "pct": 0}
                    lines.append(
                        f"| {col.name} | {col.dtype} | {col.missing_pct}% | "
                        f"{col.unique_count} | {top['value'][:20]} | {top['pct']}% |"
                    )
                lines.append("")
        
        # Correlations
        if eda.correlations and isinstance(eda.correlations, dict):
            top_pos = eda.correlations.get("top_positive", [])
            top_neg = eda.correlations.get("top_negative", [])
            
            if top_pos or top_neg:
                lines.append("## Correlations")
                lines.append("")
                
                if top_pos:
                    lines.append("### Strong Positive Correlations")
                    lines.append("")
                    lines.append("| Column 1 | Column 2 | Correlation |")
                    lines.append("|----------|----------|-------------|")
                    for c in top_pos[:5]:
                        lines.append(f"| {c['col1']} | {c['col2']} | {c['correlation']:.3f} |")
                    lines.append("")
                
                if top_neg:
                    lines.append("### Strong Negative Correlations")
                    lines.append("")
                    lines.append("| Column 1 | Column 2 | Correlation |")
                    lines.append("|----------|----------|-------------|")
                    for c in top_neg[:5]:
                        lines.append(f"| {c['col1']} | {c['col2']} | {c['correlation']:.3f} |")
                    lines.append("")
        
        # LLM Insights
        if eda.llm_insights:
            lines.append("## 🤖 AI-Generated Insights")
            lines.append("")
            lines.append(eda.llm_insights)
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Report generated by AutoDS - Multi-Agent Data Science Platform*")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, eda: EDAResult,
                               include_sample: bool = True) -> str:
        """Generate an HTML report."""
        # Convert markdown to basic HTML
        md_content = self._generate_markdown_report(eda, include_sample)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDA Report: {eda.dataset_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .warning {{ color: #e74c3c; }}
        .insight {{
            background: #ecf0f1;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 15px 0;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <pre>{md_content}</pre>
    </div>
</body>
</html>"""
        
        return html


if __name__ == "__main__":
    # Test the reporting agent
    from .eda_agent import EDAResult, ColumnStats
    
    # Create mock EDA result
    eda_result = EDAResult(
        dataset_id="test_dataset",
        success=True,
        summary_stats={
            "total_rows": 1000,
            "total_columns": 10,
            "numeric_columns": 6,
            "categorical_columns": 4,
            "missing_pct": 5.5,
            "duplicate_rows": 12,
            "memory_mb": 0.5
        },
        column_stats=[
            ColumnStats(
                name="age", dtype="int64", missing_count=0, missing_pct=0,
                unique_count=50, mean=35.5, std=12.3, min=18, max=80, median=34
            ),
            ColumnStats(
                name="category", dtype="object", missing_count=10, missing_pct=1.0,
                unique_count=3, top_values=[{"value": "A", "count": 500, "pct": 50}]
            )
        ],
        warnings=["Column 'income': Contains 15 potential outliers"],
        llm_insights="This dataset contains customer information with reasonable data quality."
    )
    
    agent = ReportingAgent()
    result = agent.run(eda_result)
    
    print(f"\nSuccess: {result.success}")
    print(f"Report path: {result.report_path}")
