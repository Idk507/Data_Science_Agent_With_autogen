"""
Base Agent class with Azure OpenAI integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from openai import AzureOpenAI

from ..config import get_config
from ..memory import get_memory


class BaseAgent(ABC):
    """Base class for all AutoDS agents."""
    
    def __init__(self, name: str):
        """Initialize the agent."""
        self.name = name
        self.config = get_config()
        self.memory = get_memory()
        self._client: Optional[AzureOpenAI] = None
    
    @property
    def llm_client(self) -> AzureOpenAI:
        """Get or create the Azure OpenAI client."""
        if self._client is None:
            cfg = self.config.azure_openai
            self._client = AzureOpenAI(
                azure_endpoint=cfg.endpoint,
                api_key=cfg.api_key,
                api_version=cfg.api_version
            )
        return self._client
    
    def call_llm(self, prompt: str, system_prompt: Optional[str] = None,
                 max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Call Azure OpenAI with the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0-1)
            
        Returns:
            LLM response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.azure_openai.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[{self.name}] LLM call failed: {e}")
            return f"Error: {e}"
    
    def log(self, message: str) -> None:
        """Log a message from this agent."""
        print(f"[{self.name}] {message}")
    
    def get_context(self, dataset_id: Optional[str] = None) -> str:
        """Get relevant context from memory."""
        return self.memory.get_context_for_agent(
            self.name.lower().replace(" ", "_"),
            dataset_id
        )
    
    def store_result(self, category: str, content: str,
                     dataset_id: Optional[str] = None,
                     metadata: Optional[dict] = None) -> str:
        """Store a result in memory."""
        return self.memory.store(
            category=category,
            content=content,
            dataset_id=dataset_id,
            metadata=metadata
        )
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the agent's main task."""
        pass
