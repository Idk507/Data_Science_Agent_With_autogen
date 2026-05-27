"""
ML Orchestrator - Multi-agent coordination using Autogen v0.4+ API.

This module orchestrates the ML pipeline by coordinating multiple
specialized agents using Autogen's team-based approach.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_core import CancellationToken
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

from .agents import (
    create_data_scientist_agent,
    create_model_builder_agent,
    create_hyperparameter_tuner_agent,
    create_evaluator_agent,
)
from .autogen_config import get_azure_model_client
from ..memory import get_memory
from ..config import get_config


class MLOrchestrator:
    """
    Orchestrates the ML pipeline using Autogen multi-agent framework (v0.4+).
    
    This class coordinates multiple specialized agents:
    - DataScientist: Analyzes data and recommends strategies
    - ModelBuilder: Writes model training code
    - HyperparameterTuner: Optimizes model parameters
    - Evaluator: Evaluates model performance
    
    The agents communicate through Autogen's RoundRobinGroupChat.
    """
    
    def __init__(self, dataset_id: str, data_path: Path):
        """
        Initialize the ML Orchestrator.
        
        Args:
            dataset_id: Unique identifier for the dataset
            data_path: Path to the dataset file
        """
        self.dataset_id = dataset_id
        self.data_path = data_path
        self.config = get_config()
        self.memory = get_memory()
        
        # Create working directory for ML artifacts
        self.work_dir = self.config.paths.artifacts_dir / f"ml_{dataset_id}"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        self._init_agents()
        
        # Conversation history for memory
        self.conversation_history: List[Dict[str, str]] = []
    
    def _init_agents(self) -> None:
        """Initialize all ML agents using v0.4+ API."""
        if not AUTOGEN_AVAILABLE:
            raise RuntimeError(
                "Autogen is not available. "
                "Install with: pip install pyautogen autogen-ext[openai]"
            )
        
        # Get model client
        self.model_client = get_azure_model_client()
        
        # Create specialized agents
        self.data_scientist = create_data_scientist_agent(self.model_client)
        self.model_builder = create_model_builder_agent(self.model_client)
        self.hyperparameter_tuner = create_hyperparameter_tuner_agent(
            self.model_client
        )
        self.evaluator = create_evaluator_agent(self.model_client)
        
        # Collect all agents
        self.agents = [
            self.data_scientist,
            self.model_builder,
            self.evaluator,
            self.hyperparameter_tuner,
        ]
        
        # Create the team using RoundRobinGroupChat
        # Rely on max_turns for termination to avoid keyword matching issues
        self.team = RoundRobinGroupChat(
            self.agents,
            max_turns=20,  # Maximum conversation rounds
        )
        
        print(f"✓ ML Orchestrator initialized with {len(self.agents)} agents")
    
    def _get_data_context(self) -> str:
        """Get context about the dataset from previous analysis."""
        # Get EDA summary from memory
        eda_context = self.memory.get_latest("eda_summary", self.dataset_id)
        ingestion_context = self.memory.get_latest(
            "ingestion_summary", self.dataset_id
        )
        
        context_parts = []
        
        if ingestion_context:
            content = ingestion_context.get('content', '')
            context_parts.append(f"Data Ingestion Summary:\n{content}")
        
        if eda_context:
            content = eda_context.get('content', '')
            context_parts.append(f"EDA Summary:\n{content}")
        
        if context_parts:
            return "\n\n".join(context_parts)
        return "No previous analysis available."
    
    def _build_initial_prompt(
        self,
        target_column: str,
        problem_type: str = "auto",
        task: str = "full_pipeline"
    ) -> str:
        """
        Build the initial prompt for the ML pipeline.
        
        Args:
            target_column: The target variable column name
            problem_type: 'classification', 'regression', or 'auto'
            task: Type of task - 'full_pipeline', 'train', 'tune', 'evaluate'
        
        Returns:
            Formatted prompt string
        """
        data_context = self._get_data_context()
        
        if task == "full_pipeline":
            task_description = """
TASK: Complete ML Pipeline

Execute the following steps:
1. DataScientist: Analyze the dataset and recommend appropriate models
2. ModelBuilder: Write complete Python code to:
   - Load and preprocess the data
   - Split into train/test sets
   - Train a baseline model
3. Evaluator: Write code to evaluate the baseline model
4. HyperparameterTuner: Write code to tune the best performing model
5. Evaluator: Final evaluation and comparison

When all steps are complete, provide a comprehensive summary of results."""
        
        elif task == "train":
            task_description = """
TASK: Model Training

Execute the following steps:
1. DataScientist: Recommend the best model for this problem
2. ModelBuilder: Write and execute code to train the model
3. Evaluator: Evaluate the trained model

When complete, provide a summary of results."""
        
        elif task == "tune":
            task_description = """
TASK: Hyperparameter Tuning

Execute the following steps:
1. HyperparameterTuner: Design and run hyperparameter optimization
2. Evaluator: Evaluate the tuned model vs baseline

When complete, provide a summary of results."""
        
        else:
            task_description = f"""
TASK: {task}

Execute the requested task."""
        
        prompt = f"""
=== ML Pipeline Request ===

DATASET INFORMATION:
- Dataset ID: {self.dataset_id}
- Data Path: {self.data_path}
- Target Column: {target_column}
- Problem Type: {problem_type}
- Working Directory: {self.work_dir}

PREVIOUS ANALYSIS:
{data_context}

{task_description}

IMPORTANT GUIDELINES:
1. Use pandas to load data from: {self.data_path}
2. Save all models to: {self.work_dir}
3. Save all plots to: {self.work_dir}
4. Print clear progress messages
5. Handle missing values appropriately
6. Use scikit-learn for all ML models
7. When tuning, use either GridSearchCV or Optuna

Let's begin! DataScientist, please start by analyzing the dataset.
"""
        return prompt
    
    async def _run_team_async(self, initial_prompt: str) -> Any:
        """Run the team asynchronously with streaming output."""
        messages = []
        
        async for event in self.team.run_stream(
            task=initial_prompt,
            cancellation_token=CancellationToken(),
        ):
            # Print messages as they come
            if hasattr(event, 'source') and hasattr(event, 'content'):
                source = event.source
                content = str(event.content)
                messages.append({"source": source, "content": content})
                
                # Print to console
                print(f"\n{'='*50}")
                print(f"🤖 [{source}]:")
                print(f"{'='*50}")
                # Print first 1000 chars
                print(content[:1000])
                if len(content) > 1000:
                    print(f"... ({len(content)} chars total)")
        
        # Return collected messages
        return messages
    
    def _store_conversation_to_memory(self, messages: list) -> None:
        """Store the conversation history to memory for follow-up."""
        try:
            if not messages:
                print("No messages to store")
                return
            
            # Format messages for storage
            formatted = []
            for msg in messages:
                if isinstance(msg, dict):
                    formatted.append({
                        "role": msg.get("source", "unknown"),
                        "content": str(msg.get("content", ""))[:500]
                    })
            
            if formatted:
                conversation_content = json.dumps(formatted, indent=2)
                
                self.memory.store(
                    category="ml_conversation",
                    content=conversation_content,
                    dataset_id=self.dataset_id,
                    metadata={
                        "num_messages": len(formatted),
                        "agents": [a.name for a in self.agents],
                    }
                )
                
                # Store summary
                summary = "\n".join([
                    f"{m['role']}: {m['content'][:200]}..."
                    for m in formatted[-5:]
                ])
                
                self.memory.store(
                    category="ml_results",
                    content=summary,
                    dataset_id=self.dataset_id,
                    metadata={"timestamp": datetime.now().isoformat()}
                )
                
                print(f"✓ Conversation stored ({len(messages)} messages)")
        except Exception as e:
            print(f"Warning: Could not store conversation: {e}")
    
    def run_pipeline(self,
                     target_column: str,
                     problem_type: str = "auto",
                     task: str = "full_pipeline") -> Dict[str, Any]:
        """
        Run the ML pipeline with the multi-agent team.
        
        Args:
            target_column: The target variable column name
            problem_type: 'classification', 'regression', or 'auto'
            task: Type of task to perform
        
        Returns:
            Dictionary containing pipeline results
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting ML Pipeline for: {self.dataset_id}")
        print(f"   Target: {target_column}")
        print(f"   Problem Type: {problem_type}")
        print(f"   Task: {task}")
        print(f"{'='*60}\n")
        
        # Build initial prompt
        initial_prompt = self._build_initial_prompt(
            target_column=target_column,
            problem_type=problem_type,
            task=task
        )
        
        # Run the team
        try:
            result = asyncio.run(self._run_team_async(initial_prompt))
            
            # Store conversation to memory
            self._store_conversation_to_memory(result)
            
        except Exception as e:
            print(f"\n⚠️ Pipeline interrupted: {e}")
            result = None
        
        # Collect results
        results = {
            "dataset_id": self.dataset_id,
            "target_column": target_column,
            "problem_type": problem_type,
            "task": task,
            "work_dir": str(self.work_dir),
            "artifacts": list(self.work_dir.glob("*")),
            "success": result is not None,
        }
        
        print(f"\n{'='*60}")
        print("✓ ML Pipeline Complete")
        print(f"  Artifacts directory: {self.work_dir}")
        print(f"{'='*60}")
        
        return results
    
    async def run_pipeline_async(self,
                                  target_column: str,
                                  problem_type: str = "auto",
                                  task: str = "full_pipeline") -> Dict[str, Any]:
        """
        Async version of run_pipeline.
        """
        print(f"\n🚀 Starting ML Pipeline for: {self.dataset_id}")
        
        initial_prompt = self._build_initial_prompt(
            target_column=target_column,
            problem_type=problem_type,
            task=task
        )
        
        try:
            result = await self._run_team_async(initial_prompt)
            self._store_conversation_to_memory(result)
        except Exception as e:
            print(f"\n⚠️ Pipeline interrupted: {e}")
            result = None
        
        return {
            "dataset_id": self.dataset_id,
            "target_column": target_column,
            "success": result is not None,
        }
        print(f"  Artifacts saved to: {self.work_dir}")
        print(f"{'='*60}\n")
        
        return results
    
    def follow_up(self, question: str) -> str:
        """
        Ask a follow-up question about the ML results.
        
        Uses memory to retrieve context from previous conversations.
        
        Args:
            question: Follow-up question
        
        Returns:
            Response from the agent team
        """
        # Get previous conversation from memory
        prev_conversation = self.memory.get_latest("ml_conversation", self.dataset_id)
        prev_results = self.memory.get_latest("ml_results", self.dataset_id)
        
        context = ""
        if prev_conversation:
            context = f"Previous ML Conversation:\n{prev_conversation.get('content', '')[:2000]}"
        if prev_results:
            context += f"\n\nPrevious Results:\n{prev_results.get('content', '')}"
        
        follow_up_prompt = f"""
FOLLOW-UP QUESTION

Previous Context:
{context}

User Question: {question}

Please answer the question based on the previous ML pipeline execution.
If you need to run additional analysis, write the code and execute it.
"""
        
        print(f"\n📝 Follow-up Question: {question}\n")
        
        try:
            self.user_proxy.initiate_chat(
                self.manager,
                message=follow_up_prompt,
            )
        except Exception as e:
            print(f"\n⚠️ Follow-up interrupted: {e}")
        
        # Get the last response
        if self.group_chat.messages:
            last_msg = self.group_chat.messages[-1]
            return last_msg.get("content", "No response generated.")
        
        return "No response generated."
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return [
            {"role": msg.get("name", "unknown"), "content": msg.get("content", "")}
            for msg in self.group_chat.messages
        ]


def run_ml_pipeline(
    dataset_id: str,
    data_path: Path,
    target_column: str,
    problem_type: str = "auto",
    task: str = "full_pipeline"
) -> Dict[str, Any]:
    """
    Convenience function to run the ML pipeline.
    
    Args:
        dataset_id: Unique identifier for the dataset
        data_path: Path to the dataset file
        target_column: Target variable column name
        problem_type: 'classification', 'regression', or 'auto'
        task: Type of task to perform
    
    Returns:
        Pipeline results dictionary
    """
    orchestrator = MLOrchestrator(dataset_id, data_path)
    return orchestrator.run_pipeline(
        target_column=target_column,
        problem_type=problem_type,
        task=task
    )


if __name__ == "__main__":
    # Test the orchestrator
    print("=== ML Orchestrator Test ===")
    
    if not AUTOGEN_AVAILABLE:
        print("✗ Autogen not available. Install with: pip install pyautogen>=0.2.0")
    else:
        # Test with demo_sales dataset
        config = get_config()
        demo_path = config.paths.data_dir / "demo_sales.csv"
        
        if demo_path.exists():
            print(f"✓ Found demo dataset: {demo_path}")
            print("\nTo run the pipeline, use:")
            print('  orchestrator = MLOrchestrator("demo_sales", demo_path)')
            print('  results = orchestrator.run_pipeline(target_column="Total", problem_type="regression")')
        else:
            print(f"✗ Demo dataset not found: {demo_path}")
