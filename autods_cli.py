#!/usr/bin/env python
"""
AutoDS CLI - Command-line interface for the Data Science Agent platform.
"""

import sys
import click
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@click.group()
@click.version_option(version="0.1.0", prog_name="AutoDS")
def cli():
    """AutoDS - Multi-Agent Data Science Platform.
    
    A local-first data science platform powered by Azure OpenAI and Autogen.
    """
    pass


@cli.command()
@click.option("--dataset", "-d", required=True, help="Dataset name from registry or path to file")
@click.option("--goal", "-g", default="eda_report", 
              type=click.Choice(["eda_report", "full_pipeline"]),
              help="Workflow goal to execute")
@click.option("--format", "-f", "report_format", default="markdown",
              type=click.Choice(["markdown", "html"]),
              help="Report output format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def run(dataset: str, goal: str, report_format: str, verbose: bool):
    """Run a data science workflow on a dataset.
    
    Examples:
    
        autods run --dataset demo_sales --goal eda_report
        
        autods run -d my_data.csv -g eda_report -f html
    """
    from autods.agents.orchestrator import run_workflow
    from autods.config import get_config
    
    # Initialize configuration
    config = get_config()
    config.initialize()
    
    click.echo(f"\n{'='*60}")
    click.echo("🤖 AutoDS - Multi-Agent Data Science Platform")
    click.echo(f"{'='*60}")
    click.echo(f"Dataset: {dataset}")
    click.echo(f"Goal: {goal}")
    click.echo(f"Report Format: {report_format}")
    click.echo("")
    
    # Check Azure OpenAI configuration
    if not config.azure_openai.is_configured:
        click.echo("⚠️  Warning: Azure OpenAI is not configured.")
        click.echo("   LLM features will be limited.")
        click.echo("   Please set API keys in .env file.")
        click.echo("")
    
    # Run the workflow
    result = run_workflow(
        dataset_id=dataset,
        goal=goal,
        report_format=report_format
    )
    
    # Display results
    click.echo("")
    click.echo(f"{'='*60}")
    if result.success:
        click.echo(click.style("✓ Workflow completed successfully!", fg="green", bold=True))
        click.echo(f"  Time: {result.execution_time_seconds:.2f} seconds")
        click.echo(f"  Stages: {', '.join(result.stages_completed)}")
        
        if result.report_result and result.report_result.report_path:
            click.echo(f"  Report: {result.report_result.report_path}")
        
        if result.eda_result and result.eda_result.warnings:
            click.echo(f"\n⚠️  Data Quality Warnings ({len(result.eda_result.warnings)}):")
            for w in result.eda_result.warnings[:5]:
                click.echo(f"   - {w}")
            if len(result.eda_result.warnings) > 5:
                click.echo(f"   ... and {len(result.eda_result.warnings) - 5} more")
    else:
        click.echo(click.style("✗ Workflow failed!", fg="red", bold=True))
        click.echo(f"  Error: {result.error}")
        if result.stages_failed:
            click.echo(f"  Failed at: {', '.join(result.stages_failed)}")
    
    click.echo(f"{'='*60}\n")
    
    return 0 if result.success else 1


@cli.command()
def datasets():
    """List all registered datasets."""
    from autods.registry import get_registry
    
    registry = get_registry()
    dataset_list = registry.list_datasets()
    
    click.echo("\n📊 Registered Datasets:")
    click.echo("-" * 40)
    
    if not dataset_list:
        click.echo("No datasets registered.")
        click.echo("Add datasets to datasets.yaml")
        return
    
    for name in dataset_list:
        info = registry.get(name)
        click.echo(f"  • {name}")
        click.echo(f"    Type: {info.source_type.value}, Format: {info.format}")
        click.echo(f"    URI: {info.uri}")
        if info.description:
            click.echo(f"    Description: {info.description}")
        click.echo("")


@cli.command()
def config():
    """Show current configuration."""
    from autods.config import get_config
    
    cfg = get_config()
    
    click.echo("\n⚙️  AutoDS Configuration:")
    click.echo("-" * 40)
    
    click.echo("\nPaths:")
    click.echo(f"  Project Root: {cfg.paths.project_root}")
    click.echo(f"  Data Dir: {cfg.paths.data_dir}")
    click.echo(f"  Reports Dir: {cfg.paths.reports_dir}")
    click.echo(f"  Artifacts Dir: {cfg.paths.artifacts_dir}")
    click.echo(f"  VectorStore: {cfg.paths.vectorstore_dir}")
    
    click.echo("\nAzure OpenAI:")
    if cfg.azure_openai.is_configured:
        click.echo(f"  ✓ Configured")
        click.echo(f"  Endpoint: {cfg.azure_openai.endpoint[:50]}...")
        click.echo(f"  Deployment: {cfg.azure_openai.deployment_name}")
        click.echo(f"  API Version: {cfg.azure_openai.api_version}")
    else:
        click.echo("  ✗ Not configured")
        click.echo("  Please set environment variables in .env file")
    
    # Validate
    issues = cfg.validate_config()
    if issues:
        click.echo("\n⚠️  Configuration Issues:")
        for issue in issues:
            click.echo(f"  - {issue}")


@cli.command()
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--dataset", "-d", default=None, help="Filter by dataset")
@click.option("--query", "-q", default=None, help="Search query")
@click.option("--limit", "-n", default=10, help="Maximum results")
def memory(category: str, dataset: str, query: str, limit: int):
    """Browse stored memories and context."""
    from autods.memory import get_memory
    
    mem = get_memory()
    
    click.echo("\n🧠 Memory Browser:")
    click.echo("-" * 40)
    
    if query:
        results = mem.search(query, n_results=limit, category=category, dataset_id=dataset)
        click.echo(f"Search results for '{query}':")
    elif category:
        results = mem.get_by_category(category, dataset_id=dataset, limit=limit)
        click.echo(f"Entries in category '{category}':")
    else:
        # Show recent entries from JSON store
        results = mem._json_store[-limit:][::-1]
        click.echo("Recent memory entries:")
    
    if not results:
        click.echo("  No entries found.")
        return
    
    for entry in results:
        cat = entry.get("category", "unknown")
        content = entry.get("content", "")[:100]
        ts = entry.get("timestamp", "")[:19]
        ds = entry.get("dataset_id", "")
        
        click.echo(f"\n  [{cat}] {ts}")
        if ds:
            click.echo(f"  Dataset: {ds}")
        click.echo(f"  {content}...")


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to clear all memory?")
def clear_memory():
    """Clear all stored memories."""
    from autods.memory import get_memory
    
    mem = get_memory()
    count = mem.clear()
    click.echo(f"✓ Cleared {count} memory entries.")


@cli.command()
def init():
    """Initialize project structure and verify configuration."""
    from autods.config import get_config
    
    click.echo("\n🔧 Initializing AutoDS...")
    click.echo("-" * 40)
    
    cfg = get_config()
    cfg.initialize()
    
    click.echo("✓ Created directory structure:")
    click.echo(f"  - {cfg.paths.data_dir}")
    click.echo(f"  - {cfg.paths.reports_dir}")
    click.echo(f"  - {cfg.paths.artifacts_dir}")
    click.echo(f"  - {cfg.paths.vectorstore_dir}")
    click.echo(f"  - {cfg.paths.memory_dir}")
    
    # Check datasets.yaml
    if cfg.paths.datasets_file.exists():
        click.echo(f"✓ Found datasets.yaml")
    else:
        click.echo(f"⚠️  datasets.yaml not found. Creating template...")
        # Create template
        template = """# AutoDS Dataset Registry
# Format: dataset_name: source_uri
# 
# Source types:
#   local:./path/to/file.csv - Local file
#   https://url.com/data.csv - URL
#
# Example:
# demo_sales: local:./data/demo_sales.csv
# external_data: https://example.com/data.csv

datasets:
  demo_sales: local:./data/demo_sales.csv
"""
        with open(cfg.paths.datasets_file, "w") as f:
            f.write(template)
        click.echo(f"✓ Created datasets.yaml template")
    
    # Validate configuration
    issues = cfg.validate_config()
    if issues:
        click.echo("\n⚠️  Configuration issues to resolve:")
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("\n✓ Configuration valid!")
    
    click.echo("\n🚀 Ready to run workflows!")
    click.echo("   Try: python autods_cli.py run --dataset demo_sales --goal eda_report")


# ============================================================================
# ML Training Commands (Autogen Multi-Agent Framework)
# ============================================================================

@cli.command()
@click.option("--dataset", "-d", required=True, help="Dataset name from registry or path to file")
@click.option("--target", "-t", required=True, help="Target column for prediction")
@click.option("--problem-type", "-p", default="auto",
              type=click.Choice(["auto", "classification", "regression"]),
              help="ML problem type (auto-detect if not specified)")
@click.option("--task", default="full_pipeline",
              type=click.Choice(["full_pipeline", "train", "tune", "evaluate"]),
              help="ML task to perform")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def train(dataset: str, target: str, problem_type: str, task: str, verbose: bool):
    """Train ML models using Autogen multi-agent framework.
    
    This command launches a multi-agent ML pipeline that:
    - Analyzes the dataset (DataScientist agent)
    - Writes and executes training code (ModelBuilder + CodeExecutor)
    - Optimizes hyperparameters (HyperparameterTuner agent)
    - Evaluates model performance (Evaluator agent)
    
    Examples:
    
        autods train --dataset demo_sales --target Total --problem-type regression
        
        autods train -d titanic -t Survived -p classification
        
        autods train -d my_data.csv -t target --task tune
    """
    from autods.config import get_config
    from autods.registry import get_registry
    from autods.storage import get_storage_client
    
    # Initialize configuration
    config = get_config()
    config.initialize()
    
    click.echo(f"\n{'='*60}")
    click.echo("🤖 AutoDS ML Training - Multi-Agent Framework")
    click.echo(f"{'='*60}")
    click.echo(f"Dataset: {dataset}")
    click.echo(f"Target Column: {target}")
    click.echo(f"Problem Type: {problem_type}")
    click.echo(f"Task: {task}")
    click.echo("")
    
    # Check Azure OpenAI configuration
    if not config.azure_openai.is_configured:
        click.echo(click.style("✗ Error: Azure OpenAI is not configured.", fg="red"))
        click.echo("  ML training requires Azure OpenAI for agent coordination.")
        click.echo("  Please set API keys in .env file.")
        return 1
    
    # Resolve dataset path
    registry = get_registry()
    dataset_info = registry.get(dataset)
    storage = get_storage_client()
    
    if dataset_info:
        click.echo(f"✓ Found dataset in registry: {dataset}")
        # Get the data path from the dataset info
        if dataset_info.source_type.value == "local":
            data_path = Path(dataset_info.uri)
            if not data_path.is_absolute():
                data_path = config.paths.project_root / data_path
        else:
            # For URL sources, download and save locally
            data = storage.load_dataframe(dataset_info)
            data_path = config.paths.data_dir / f"{dataset}.csv"
            data.to_csv(data_path, index=False)
    else:
        # Try as direct path
        data_path = Path(dataset)
        if not data_path.exists():
            click.echo(click.style(f"✗ Error: Dataset not found: {dataset}", fg="red"))
            return 1
    
    click.echo(f"✓ Data path: {data_path}")
    
    # Import and run ML orchestrator
    try:
        from autods.ml_agents import MLOrchestrator
        
        click.echo("\n🚀 Launching multi-agent ML pipeline...")
        click.echo("   Agents: DataScientist, ModelBuilder,")
        click.echo("           HyperparameterTuner, Evaluator")
        click.echo("")
        
        orchestrator = MLOrchestrator(dataset_id=dataset, data_path=data_path)
        results = orchestrator.run_pipeline(
            target_column=target,
            problem_type=problem_type,
            task=task
        )
        
        # Display results
        click.echo("")
        click.echo(f"{'='*60}")
        if results.get('success', False):
            click.echo(click.style("✓ ML Pipeline Complete!", fg="green", bold=True))
        else:
            click.echo(click.style("⚠️ ML Pipeline finished with issues", fg="yellow"))
        click.echo(f"  Artifacts saved to: {results['work_dir']}")
        
        if results['artifacts']:
            click.echo(f"\n  Generated artifacts:")
            for artifact in results['artifacts']:
                click.echo(f"    - {artifact.name}")
        
        click.echo(f"{'='*60}\n")
        
    except ImportError as e:
        click.echo(click.style(f"✗ Import Error: {e}", fg="red"))
        click.echo("  Please install required packages: pip install pyautogen>=0.2.0")
        return 1
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


@cli.command()
@click.option("--dataset", "-d", required=True, help="Dataset to ask about")
@click.argument("question")
def ask(dataset: str, question: str):
    """Ask a follow-up question about ML results.
    
    Uses memory to retrieve context from previous ML pipeline runs.
    
    Examples:
    
        autods ask -d demo_sales "What was the best model?"
        
        autods ask -d titanic "How can I improve the accuracy?"
    """
    from autods.memory import get_memory
    from autods.config import get_config
    
    config = get_config()
    memory = get_memory()
    
    click.echo(f"\n🔍 Looking up context for: {dataset}")
    
    # Get ML context
    context = memory.get_ml_context(dataset)
    
    if "No ML context available" in context:
        click.echo(click.style("⚠️  No previous ML results found for this dataset.", fg="yellow"))
        click.echo("   Run `autods train` first to generate ML results.")
        return 1
    
    click.echo(f"✓ Found previous context")
    click.echo(f"\n📝 Question: {question}\n")
    
    try:
        from autods.ml_agents import MLOrchestrator
        
        # Create orchestrator for follow-up
        data_path = config.paths.data_dir / f"{dataset}.csv"
        if not data_path.exists():
            # Try to find in artifacts
            data_path = config.paths.artifacts_dir / f"ml_{dataset}" / "data.csv"
        
        orchestrator = MLOrchestrator(dataset_id=dataset, data_path=data_path)
        response = orchestrator.follow_up(question)
        
        click.echo(f"\n💬 Response:\n{response}")
        
    except Exception as e:
        # Fallback: Just show the context
        click.echo(f"⚠️  Could not start agent conversation: {e}")
        click.echo(f"\n📋 Available Context:\n{context[:2000]}...")
    
    return 0


@cli.command()
@click.option("--dataset", "-d", default=None, help="Filter by dataset")
def ml_history(dataset: str):
    """Show ML pipeline history and results."""
    from autods.memory import get_memory
    
    memory = get_memory()
    
    click.echo("\n📊 ML Pipeline History:")
    click.echo("-" * 40)
    
    # Get ML results
    results = memory.get_by_category("ml_results", dataset_id=dataset, limit=10)
    
    if not results:
        click.echo("No ML pipeline runs found.")
        click.echo("Run `autods train` to start an ML pipeline.")
        return
    
    for result in results:
        ts = result.get("timestamp", "")[:19]
        ds = result.get("dataset_id", "unknown")
        content = result.get("content", "")[:200]
        
        click.echo(f"\n🔬 {ds} - {ts}")
        click.echo(f"   {content}...")
    
    # Get conversations
    conversations = memory.get_recent_conversations(dataset_id=dataset, limit=5)
    
    if conversations:
        click.echo(f"\n💬 Recent Conversations:")
        for conv in conversations:
            click.echo(f"  - {conv['session_id']}: {conv['num_messages']} messages ({conv['timestamp'][:19]})")


if __name__ == "__main__":
    cli()
