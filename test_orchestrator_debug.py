"""Debug test to see what's happening with the orchestrator."""
import asyncio
import sys
sys.path.insert(0, "c:\\Users\\dhanu\\Downloads\\Data_Science_Agent_With_autogen")

from autods.ml_agents.autogen_config import get_azure_model_client

async def test_orchestrator_run():
    """Test the exact flow used in the orchestrator."""
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_core import CancellationToken
    
    # Create model client exactly as orchestrator does
    print("Creating Azure model client...")
    model_client = get_azure_model_client()
    print(f"  Client type: {type(model_client)}")
    
    # Create a simple agent like the orchestrator does
    print("\nCreating agent...")
    agent = AssistantAgent(
        name="TestAgent",
        model_client=model_client,
        system_message="You are a helpful assistant. Keep responses brief.",
    )
    print(f"  Agent: {agent.name}")
    
    # Create team exactly as orchestrator does
    print("\nCreating team...")
    team = RoundRobinGroupChat(
        participants=[agent],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=20,
    )
    print(f"  Team: {team}")
    
    # Run with the same prompt pattern
    print("\n" + "="*60)
    print("Running team with a simple task...")
    print("="*60)
    
    messages = []
    task = "Hello! Please respond with 'I am working correctly' if you can see this message."
    
    async for event in team.run_stream(
        task=task,
        cancellation_token=CancellationToken(),
    ):
        event_type = type(event).__name__
        print(f"\n>>> Event type: {event_type}")
        
        if hasattr(event, 'source') and hasattr(event, 'content'):
            source = event.source
            content = str(event.content)
            messages.append({"source": source, "content": content})
            print(f">>> Source: {source}")
            print(f">>> Content: {content[:500]}")
        
        if hasattr(event, 'stop_reason'):
            print(f">>> Stop reason: {event.stop_reason}")
    
    print("\n" + "="*60)
    print(f"Total messages collected: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"  {i+1}. [{msg['source']}]: {msg['content'][:100]}...")
    print("="*60)
    
    return messages

if __name__ == "__main__":
    result = asyncio.run(test_orchestrator_run())
    print(f"\nFinal result: {len(result)} messages")
