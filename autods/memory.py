"""
Memory System - ChromaDB-based persistent memory for context and knowledge retrieval.

Supports:
- Semantic search for relevant context
- Structured JSON storage for metadata
- Conversation history for follow-up questions
- ML pipeline results tracking
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, List, Dict
from pydantic import BaseModel

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not installed. Memory features will be limited.")

from .config import get_config


class MemoryEntry(BaseModel):
    """A single memory entry."""
    id: str
    category: str  # e.g., "eda_summary", "model_metrics", "cleaning_steps"
    dataset_id: Optional[str] = None
    content: str  # Main text content
    metadata: dict = {}  # Additional structured data
    timestamp: str = ""
    
    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.now().isoformat()
        if not data.get("id"):
            # Generate ID from content hash
            content_hash = hashlib.md5(
                f"{data.get('category', '')}{data.get('content', '')}{data.get('timestamp', '')}".encode()
            ).hexdigest()[:12]
            data["id"] = f"{data.get('category', 'mem')}_{content_hash}"
        super().__init__(**data)


class MemoryManager:
    """
    Manages long-term memory using ChromaDB for semantic search
    and JSON files for structured storage.
    """
    
    def __init__(self):
        """Initialize the memory manager."""
        self.config = get_config()
        self.config.paths.ensure_dirs()
        
        self._chroma_client = None
        self._collection = None
        self._json_store_path = self.config.paths.memory_dir / "memory_store.json"
        self._json_store: list[dict] = []
        
        self._init_stores()
    
    def _init_stores(self) -> None:
        """Initialize storage backends."""
        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE:
            try:
                self._chroma_client = chromadb.PersistentClient(
                    path=str(self.config.paths.vectorstore_dir)
                )
                self._collection = self._chroma_client.get_or_create_collection(
                    name="autods_memory",
                    metadata={"description": "AutoDS agent memory and context"}
                )
                print(f"✓ ChromaDB initialized at {self.config.paths.vectorstore_dir}")
            except Exception as e:
                print(f"Warning: ChromaDB initialization failed: {e}")
                self._chroma_client = None
        
        # Load JSON store
        if self._json_store_path.exists():
            try:
                with open(self._json_store_path, "r") as f:
                    self._json_store = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load JSON store: {e}")
                self._json_store = []
    
    def _save_json_store(self) -> None:
        """Save JSON store to disk."""
        try:
            with open(self._json_store_path, "w") as f:
                json.dump(self._json_store, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save JSON store: {e}")
    
    def add(self, entry: MemoryEntry) -> str:
        """
        Add a memory entry.
        
        Args:
            entry: MemoryEntry to store
            
        Returns:
            Entry ID
        """
        entry_dict = entry.model_dump()
        
        # Add to JSON store
        self._json_store.append(entry_dict)
        self._save_json_store()
        
        # Add to ChromaDB for semantic search
        if self._collection is not None:
            try:
                self._collection.add(
                    ids=[entry.id],
                    documents=[entry.content],
                    metadatas=[{
                        "category": entry.category,
                        "dataset_id": entry.dataset_id or "",
                        "timestamp": entry.timestamp,
                        **{k: str(v) for k, v in entry.metadata.items()}
                    }]
                )
            except Exception as e:
                print(f"Warning: Failed to add to ChromaDB: {e}")
        
        return entry.id
    
    def store(self, category: str, content: str, 
              dataset_id: Optional[str] = None,
              metadata: Optional[dict] = None) -> str:
        """
        Convenience method to store a memory entry.
        
        Args:
            category: Entry category (e.g., "eda_summary")
            content: Text content
            dataset_id: Optional associated dataset
            metadata: Optional additional metadata
            
        Returns:
            Entry ID
        """
        entry = MemoryEntry(
            category=category,
            content=content,
            dataset_id=dataset_id,
            metadata=metadata or {}
        )
        return self.add(entry)
    
    def search(self, query: str, n_results: int = 5, 
               category: Optional[str] = None,
               dataset_id: Optional[str] = None) -> list[dict]:
        """
        Search memory using semantic similarity.
        
        Args:
            query: Search query
            n_results: Maximum number of results
            category: Optional category filter
            dataset_id: Optional dataset filter
            
        Returns:
            List of matching memory entries
        """
        results = []
        
        # Search ChromaDB if available
        if self._collection is not None:
            try:
                where_filter = {}
                if category:
                    where_filter["category"] = category
                if dataset_id:
                    where_filter["dataset_id"] = dataset_id
                
                search_results = self._collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter if where_filter else None
                )
                
                if search_results and search_results["documents"]:
                    for i, doc in enumerate(search_results["documents"][0]):
                        results.append({
                            "id": search_results["ids"][0][i] if search_results["ids"] else None,
                            "content": doc,
                            "metadata": search_results["metadatas"][0][i] if search_results["metadatas"] else {},
                            "distance": search_results["distances"][0][i] if search_results.get("distances") else None
                        })
            except Exception as e:
                print(f"Warning: ChromaDB search failed: {e}")
        
        # Fallback to JSON store simple search if no results
        if not results:
            for entry in self._json_store:
                if category and entry.get("category") != category:
                    continue
                if dataset_id and entry.get("dataset_id") != dataset_id:
                    continue
                if query.lower() in entry.get("content", "").lower():
                    results.append(entry)
                    if len(results) >= n_results:
                        break
        
        return results
    
    def get_by_category(self, category: str, 
                        dataset_id: Optional[str] = None,
                        limit: int = 10) -> list[dict]:
        """Get all entries by category."""
        results = []
        for entry in reversed(self._json_store):  # Most recent first
            if entry.get("category") == category:
                if dataset_id is None or entry.get("dataset_id") == dataset_id:
                    results.append(entry)
                    if len(results) >= limit:
                        break
        return results
    
    def get_latest(self, category: str, 
                   dataset_id: Optional[str] = None) -> Optional[dict]:
        """Get the most recent entry for a category."""
        results = self.get_by_category(category, dataset_id, limit=1)
        return results[0] if results else None
    
    def get_context_for_agent(self, agent_name: str, 
                              dataset_id: Optional[str] = None,
                              max_entries: int = 5) -> str:
        """
        Get relevant context for an agent.
        
        Args:
            agent_name: Name of the agent requesting context
            dataset_id: Optional dataset being processed
            max_entries: Maximum number of context entries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Get relevant categories based on agent
        category_map = {
            "eda_agent": ["ingestion_summary", "eda_summary", "data_warnings"],
            "cleaning_agent": ["eda_summary", "data_warnings", "cleaning_steps"],
            "feature_agent": ["cleaning_steps", "feature_engineering"],
            "model_agent": ["feature_engineering", "model_metrics"],
            "reporting_agent": ["eda_summary", "model_metrics", "explainability"]
        }
        
        categories = category_map.get(agent_name, ["eda_summary"])
        
        for category in categories:
            entries = self.get_by_category(category, dataset_id, limit=2)
            for entry in entries:
                context_parts.append(
                    f"[{entry.get('category', 'unknown')}] {entry.get('content', '')[:500]}"
                )
        
        if not context_parts:
            return "No previous context available."
        
        return "\n\n".join(context_parts[:max_entries])
    
    def clear(self, category: Optional[str] = None) -> int:
        """
        Clear memory entries.
        
        Args:
            category: Optional category to clear (clears all if None)
            
        Returns:
            Number of entries cleared
        """
        count = 0
        
        if category:
            self._json_store = [
                e for e in self._json_store 
                if e.get("category") != category
            ]
        else:
            count = len(self._json_store)
            self._json_store = []
        
        self._save_json_store()
        
        # Clear ChromaDB
        if self._collection is not None and not category:
            try:
                # Recreate collection to clear it
                self._chroma_client.delete_collection("autods_memory")
                self._collection = self._chroma_client.create_collection(
                    name="autods_memory",
                    metadata={"description": "AutoDS agent memory and context"}
                )
            except Exception as e:
                print(f"Warning: Failed to clear ChromaDB: {e}")
        
        return count
    
    # =========================================================================
    # Conversation Memory Methods for ML Pipeline Follow-up
    # =========================================================================
    
    def store_conversation(self, 
                           session_id: str,
                           messages: list[dict],
                           dataset_id: Optional[str] = None,
                           metadata: Optional[dict] = None) -> str:
        """
        Store a complete conversation for follow-up.
        
        Args:
            session_id: Unique session identifier
            messages: List of message dictionaries with 'role' and 'content'
            dataset_id: Optional associated dataset
            metadata: Optional additional metadata
        
        Returns:
            Entry ID
        """
        content = json.dumps(messages, indent=2)
        meta = metadata or {}
        meta["session_id"] = session_id
        meta["num_messages"] = len(messages)
        
        return self.store(
            category="conversation",
            content=content,
            dataset_id=dataset_id,
            metadata=meta
        )
    
    def get_conversation(self, 
                         session_id: str,
                         dataset_id: Optional[str] = None) -> Optional[list[dict]]:
        """
        Retrieve a stored conversation.
        
        Args:
            session_id: The session ID to retrieve
            dataset_id: Optional dataset filter
        
        Returns:
            List of message dictionaries or None
        """
        entries = self.get_by_category("conversation", dataset_id, limit=50)
        
        for entry in entries:
            if entry.get("metadata", {}).get("session_id") == session_id:
                try:
                    return json.loads(entry.get("content", "[]"))
                except json.JSONDecodeError:
                    return None
        
        return None
    
    def get_recent_conversations(self, 
                                  dataset_id: Optional[str] = None,
                                  limit: int = 5) -> list[dict]:
        """
        Get recent conversation summaries.
        
        Args:
            dataset_id: Optional dataset filter
            limit: Maximum number of conversations
        
        Returns:
            List of conversation metadata
        """
        entries = self.get_by_category("conversation", dataset_id, limit=limit)
        
        summaries = []
        for entry in entries:
            meta = entry.get("metadata", {})
            summaries.append({
                "session_id": meta.get("session_id", "unknown"),
                "dataset_id": entry.get("dataset_id"),
                "num_messages": meta.get("num_messages", 0),
                "timestamp": entry.get("timestamp"),
            })
        
        return summaries
    
    def search_conversations(self, 
                              query: str,
                              dataset_id: Optional[str] = None,
                              n_results: int = 3) -> list[dict]:
        """
        Search conversations semantically.
        
        Args:
            query: Search query
            dataset_id: Optional dataset filter
            n_results: Maximum results
        
        Returns:
            List of matching conversation entries
        """
        return self.search(
            query=query,
            n_results=n_results,
            category="conversation",
            dataset_id=dataset_id
        )
    
    def get_ml_context(self, dataset_id: str) -> str:
        """
        Get complete ML context for follow-up questions.
        
        Gathers all relevant ML information from memory.
        
        Args:
            dataset_id: The dataset to get context for
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Get EDA summary
        eda = self.get_latest("eda_summary", dataset_id)
        if eda:
            context_parts.append(f"=== EDA Summary ===\n{eda.get('content', '')}")
        
        # Get ML results
        ml_results = self.get_latest("ml_results", dataset_id)
        if ml_results:
            context_parts.append(f"=== ML Results ===\n{ml_results.get('content', '')}")
        
        # Get model metrics
        metrics = self.get_latest("model_metrics", dataset_id)
        if metrics:
            context_parts.append(f"=== Model Metrics ===\n{metrics.get('content', '')}")
        
        # Get recent conversation
        conversation = self.get_latest("ml_conversation", dataset_id)
        if conversation:
            # Only include last few messages for context
            try:
                messages = json.loads(conversation.get("content", "[]"))
                recent = messages[-10:] if len(messages) > 10 else messages
                conv_text = "\n".join([
                    f"{m.get('role', 'unknown')}: {m.get('content', '')[:300]}..."
                    for m in recent
                ])
                context_parts.append(f"=== Recent Conversation ===\n{conv_text}")
            except:
                pass
        
        if not context_parts:
            return "No ML context available for this dataset."
        
        return "\n\n".join(context_parts)


# Global memory manager instance
_memory: Optional[MemoryManager] = None


def get_memory() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory
    if _memory is None:
        _memory = MemoryManager()
    return _memory


if __name__ == "__main__":
    # Test memory system
    memory = get_memory()
    print("=== Memory System Test ===")
    
    # Store some test entries
    memory.store(
        category="eda_summary",
        content="Dataset has 1000 rows and 15 columns. 3 columns have >10% missing values.",
        dataset_id="test_dataset",
        metadata={"rows": 1000, "cols": 15}
    )
    
    memory.store(
        category="data_warnings",
        content="Column 'age' has outliers beyond 3 standard deviations.",
        dataset_id="test_dataset"
    )
    
    # Search
    results = memory.search("missing values", n_results=3)
    print(f"\nSearch results for 'missing values':")
    for r in results:
        print(f"  - {r.get('content', '')[:100]}...")
    
    # Get context
    context = memory.get_context_for_agent("eda_agent", "test_dataset")
    print(f"\nContext for EDA agent:\n{context}")
