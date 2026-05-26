"""Test the actual orchestrator directly."""
import asyncio
import sys
import traceback
sys.path.insert(0, r"c:\Users\dhanu\Downloads\Data_Science_Agent_With_autogen")

from pathlib import Path
from autods.ml_agents.ml_orchestrator import MLOrchestrator
from autogen_core import CancellationToken


async def test_real_orchestrator():
    """Test the real orchestrator."""
    data_path = Path(r"c:\Users\dhanu\Downloads\Data_Science_Agent_With_autogen\data\demo_sales.csv")
    
    print("Creating MLOrchestrator...")
    orch = MLOrchestrator("demo_sales", data_path)
    
    print(f"Agents: {[a.name for a in orch.agents]}")
    print(f"Team: {orch.team}")
    
    # Use a simple test prompt - DON'T include TERMINATE in the prompt!
    test_prompt = "Hello! DataScientist please say hello."
    
    print("\nRunning team directly (bypassing _run_team_async)...")
    print("=" * 60)
    
    messages = []
    try:
        async for event in orch.team.run_stream(
            task=test_prompt,
            cancellation_token=CancellationToken(),
        ):
            event_type = type(event).__name__
            print(f">>> Event: {event_type}")
            
            if hasattr(event, 'source') and hasattr(event, 'content'):
                source = event.source
                content = str(event.content)
                messages.append({"source": source, "content": content})
                print(f">>> [{source}]: {content[:200]}")
            
            if hasattr(event, 'stop_reason'):
                print(f">>> Stop reason: {event.stop_reason}")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
    
    print("=" * 60)
    print(f"\nTotal messages: {len(messages)}")


if __name__ == "__main__":
    asyncio.run(test_real_orchestrator())
