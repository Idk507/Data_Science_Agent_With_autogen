"""
Specialized Autogen Agents for ML Pipeline (v0.4+ API).

This module defines the specialized agents for the ML pipeline using
the new Autogen agentchat framework:
- DataScientistAgent: Analyzes data and recommends ML strategies
- ModelBuilderAgent: Writes model training code
- HyperparameterTunerAgent: Optimizes model hyperparameters
- EvaluatorAgent: Evaluates model performance
"""

from typing import Optional, Any

try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("Warning: autogen-agentchat not installed.")

from .autogen_config import get_azure_model_client


# System prompts for each specialized agent
DATA_SCIENTIST_SYSTEM_MESSAGE = """You are a Senior Data Scientist agent specialized in machine learning strategy.

Your responsibilities:
1. Analyze dataset characteristics (types, distributions, missing values)
2. Recommend appropriate ML algorithms based on the problem type
3. Suggest feature engineering strategies
4. Guide the overall ML pipeline approach
5. Interpret results and provide insights

When analyzing data:
- Always start with understanding the target variable and problem type (classification/regression)
- Consider data quality issues and preprocessing needs
- Recommend models suitable for the data size and complexity
- Provide clear, actionable recommendations

IMPORTANT: You provide strategic guidance and analysis. When you recommend code,
ensure it is complete and executable by the code execution agent."""


MODEL_BUILDER_SYSTEM_MESSAGE = """You are a Machine Learning Engineer agent specialized in model building.

Your responsibilities:
1. Write clean, production-quality Python code for ML models
2. Implement data preprocessing pipelines
3. Build and train scikit-learn models
4. Create proper train/test splits
5. Handle model serialization

Code guidelines:
- Use scikit-learn for all ML models
- Always use pandas for data manipulation
- Include proper error handling
- Print clear output messages for tracking progress
- Save models using joblib

When writing code:
- Start with necessary imports at the top
- Use clear variable names
- Add comments explaining key steps
- Always print model performance metrics

Output your code in a Python code block like:
```python
# Your code here
```

IMPORTANT: Write complete, executable code."""


HYPERPARAMETER_TUNER_SYSTEM_MESSAGE = """You are a Hyperparameter Optimization agent specialized in model tuning.

Your responsibilities:
1. Design hyperparameter search spaces for ML models
2. Implement Grid Search or Optuna-based optimization
3. Balance exploration vs exploitation in search
4. Report best parameters and improvement metrics

Code guidelines:
- Use Optuna for complex optimization (preferred)
- Use GridSearchCV for simpler searches
- Always use cross-validation
- Report training time and best score
- Save the best model

When writing code:
- Import optuna or sklearn.model_selection as needed
- Define clear objective functions for Optuna
- Use reasonable n_trials (start with 20-50)
- Print progress and final best parameters

Output your code in a Python code block like:
```python
# Your code here
```

IMPORTANT: Write complete, executable code for hyperparameter tuning."""


EVALUATOR_SYSTEM_MESSAGE = """You are a Model Evaluation agent specialized in ML metrics and validation.

Your responsibilities:
1. Calculate comprehensive evaluation metrics
2. Generate classification reports or regression metrics
3. Create confusion matrices and ROC curves
4. Perform cross-validation analysis
5. Compare model performances

Code guidelines:
- Use sklearn.metrics for all evaluations
- For classification: accuracy, precision, recall, F1, ROC-AUC
- For regression: MAE, MSE, RMSE, R²
- Generate visualizations using matplotlib
- Save plots to file

When writing code:
- Import necessary metrics from sklearn
- Print formatted results tables
- Create and save visualizations
- Provide interpretation of results

Output your code in a Python code block like:
```python
# Your code here
```

IMPORTANT: Write complete evaluation code with clear metric outputs."""


def create_data_scientist_agent(model_client: Any) -> Optional[Any]:
    """Create the Data Scientist agent for ML strategy."""
    if not AUTOGEN_AVAILABLE:
        return None
    
    return AssistantAgent(
        name="DataScientist",
        description="A senior data scientist who analyzes data and recommends ML strategies.",
        system_message=DATA_SCIENTIST_SYSTEM_MESSAGE,
        model_client=model_client,
    )


def create_model_builder_agent(model_client: Any) -> Optional[Any]:
    """Create the Model Builder agent for writing ML code."""
    if not AUTOGEN_AVAILABLE:
        return None
    
    return AssistantAgent(
        name="ModelBuilder",
        description="An ML engineer who writes model training code.",
        system_message=MODEL_BUILDER_SYSTEM_MESSAGE,
        model_client=model_client,
    )


def create_hyperparameter_tuner_agent(model_client: Any) -> Optional[Any]:
    """Create the Hyperparameter Tuner agent."""
    if not AUTOGEN_AVAILABLE:
        return None
    
    return AssistantAgent(
        name="HyperparameterTuner",
        description="A specialist in hyperparameter optimization.",
        system_message=HYPERPARAMETER_TUNER_SYSTEM_MESSAGE,
        model_client=model_client,
    )


def create_evaluator_agent(model_client: Any) -> Optional[Any]:
    """Create the Evaluator agent for model evaluation."""
    if not AUTOGEN_AVAILABLE:
        return None
    
    return AssistantAgent(
        name="Evaluator",
        description="A model evaluation specialist.",
        system_message=EVALUATOR_SYSTEM_MESSAGE,
        model_client=model_client,
    )


def get_termination_condition():
    """Get the termination condition for the group chat."""
    if not AUTOGEN_AVAILABLE:
        return None
    return TextMentionTermination("TERMINATE")


if __name__ == "__main__":
    print("=== ML Agents Test (v0.4+) ===")
    
    if not AUTOGEN_AVAILABLE:
        print("✗ Autogen not available. Install with: pip install pyautogen autogen-ext[openai]")
    else:
        print("✓ Autogen is available")
        
        try:
            model_client = get_azure_model_client()
            print("✓ Azure OpenAI model client created")
            
            # Test agent creation
            agents_info = [
                ("DataScientist", create_data_scientist_agent),
                ("ModelBuilder", create_model_builder_agent),
                ("HyperparameterTuner", create_hyperparameter_tuner_agent),
                ("Evaluator", create_evaluator_agent),
            ]
            
            for name, factory in agents_info:
                try:
                    agent = factory(model_client)
                    if agent:
                        print(f"  ✓ {name} agent created successfully")
                    else:
                        print(f"  ✗ {name} agent creation returned None")
                except Exception as e:
                    print(f"  ✗ {name} agent creation failed: {e}")
                    
        except Exception as e:
            print(f"✗ Failed to create model client: {e}")
