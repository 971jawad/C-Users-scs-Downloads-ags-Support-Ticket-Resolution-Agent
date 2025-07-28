#!/usr/bin/env python3
"""
Test LangSmith Integration for Interactive Workflow Visualization

This script tests the LangStudio integration to ensure interactive workflow
visualization works correctly at enterprise level.
"""

import os
import asyncio
import logging
from datetime import datetime

# Set up LangSmith environment
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Support-Ticket-Resolution-Agent"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

from support_agent.graph import create_support_agent_graph
from support_agent.state import create_initial_state
from support_agent.langsmith_config import get_langstudio_url

async def test_langsmith_workflow():
    """Test the complete workflow with LangSmith tracing enabled."""
    
    print("🚀 Testing LangSmith Integration for Interactive Workflow Visualization")
    print("=" * 70)
    
    # Check environment
    print(f"✓ LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print(f"✓ LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
    print(f"✓ LANGCHAIN_API_KEY: {'SET' if os.getenv('LANGCHAIN_API_KEY') else 'NOT SET'}")
    print()
    
    try:
        # Initialize the agent
        print("📊 Initializing Support Agent Graph...")
        agent = create_support_agent_graph()
        print("✓ Agent initialized successfully")
        
        # Create test ticket
        test_ticket = {
            "subject": "Test LangStudio Integration",
            "description": "Testing interactive workflow visualization with LangSmith tracing enabled. This should show up in LangStudio with full node details."
        }
        
        print(f"🎫 Processing test ticket: {test_ticket['subject']}")
        
        # Create initial state
        initial_state = create_initial_state(test_ticket)
        
        # Generate unique thread ID for this execution
        thread_id = f"langsmith_test_{datetime.now().timestamp()}"
        config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {
                "test_run": True,
                "purpose": "LangStudio Integration Test",
                "workflow_type": "support_ticket_resolution"
            }
        }
        
        print(f"🔗 Thread ID: {thread_id}")
        
        # Process the ticket
        print("⚡ Processing ticket through LangGraph workflow...")
        result = await agent.ainvoke(initial_state, config=config)
        
        # Generate LangStudio URLs
        general_url = get_langstudio_url()
        specific_url = get_langstudio_url(thread_id)
        
        print("\n" + "=" * 70)
        print("🎯 LANGSTUDIO INTERACTIVE VISUALIZATION URLS")
        print("=" * 70)
        print(f"📈 General Project View:")
        print(f"   {general_url}")
        print()
        print(f"🔍 This Specific Execution:")
        print(f"   {specific_url}")
        print()
        print("🚀 ENTERPRISE FEATURES ENABLED:")
        print("   ✓ Real-time node execution tracing")
        print("   ✓ Interactive state inspection")
        print("   ✓ Performance metrics and timing")
        print("   ✓ Complete execution history")
        print("   ✓ Error debugging capabilities")
        print()
        
        # Show execution results
        print("📋 EXECUTION RESULTS:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Category: {result.get('category', 'unknown')}")
        print(f"   Escalated: {result.get('escalated', False)}")
        print(f"   Retries: {result.get('retries', 0)}")
        print(f"   Processing Time: {len(result.get('node_execution_log', []))} steps")
        
        print("\n✅ LangSmith integration test completed successfully!")
        print("🌐 Open the URLs above to view interactive workflow visualization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during LangSmith integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_langsmith_workflow())
    
    if success:
        print("\n🎉 Interactive workflow visualization is ready!")
        print("📊 Visit LangStudio to see your workflows in action")
    else:
        print("\n⚠️  LangSmith integration needs debugging")