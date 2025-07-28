#!/usr/bin/env python3
"""
LangStudio Enterprise Workflow Visualization Setup

This script configures the support agent for interactive enterprise-level 
monitoring through LangChain Studio, providing real-time execution traces,
timing data, state changes, and decision logic visualization.
"""

import os
import asyncio
from datetime import datetime
from support_agent.graph import create_support_agent_graph
from support_agent.state import create_initial_state
from support_agent.langsmith_config import get_langstudio_url, setup_langsmith_monitoring
import uuid

def setup_enterprise_visualization():
    """Configure LangStudio for enterprise-level workflow monitoring."""
    print("🎯 Setting up LangStudio Enterprise Workflow Visualization")
    print("=" * 60)
    
    # Configure LangSmith for interactive monitoring
    langsmith_enabled = setup_langsmith_monitoring()
    
    if langsmith_enabled:
        print("✅ LangSmith configured for enterprise monitoring")
        project_url = "https://smith.langchain.com/o/1acbd1a3-5fab-4e23-8d1b-5dc5c014d2c3/projects/p/Support-Ticket-Resolution-Agent"
        print(f"📊 Interactive Dashboard: {project_url}")
        print()
        print("🔍 Enterprise Features Available:")
        print("  • Real-time execution traces")
        print("  • Node-by-node timing analysis") 
        print("  • State changes visualization")
        print("  • Decision logic flow")
        print("  • Error tracking and debugging")
        print("  • Performance metrics")
        print("  • Retry pattern analysis")
        print()
    else:
        print("⚠️  LangSmith API key needed for enterprise visualization")
        print("   Add LANGCHAIN_API_KEY to enable interactive monitoring")
    
    return langsmith_enabled

async def demonstrate_interactive_workflow():
    """Run a demo ticket to populate LangStudio with interactive data."""
    print("🚀 Running Demo Ticket for Interactive Visualization")
    print("=" * 50)
    
    # Initialize the agent
    agent = create_support_agent_graph()
    
    # Create demo ticket
    demo_ticket = {
        "subject": "Enterprise Workflow Visualization Demo",
        "description": "This is a demonstration ticket to showcase the interactive LangStudio workflow visualization with enterprise-level monitoring capabilities including execution traces, timing data, and decision logic."
    }
    
    print(f"🎫 Processing: {demo_ticket['subject']}")
    
    # Create initial state
    initial_state = create_initial_state(demo_ticket)
    
    # Generate UUID for this execution
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {
            "demo_run": True,
            "purpose": "Enterprise Visualization Demo",
            "workflow_type": "support_ticket_resolution",
            "monitoring_level": "enterprise"
        }
    }
    
    # Get LangStudio URL for this specific execution
    execution_url = get_langstudio_url(thread_id)
    print(f"📊 Live Execution Trace: {execution_url}")
    
    try:
        # Process the ticket
        start_time = datetime.now()
        result = await agent.ainvoke(initial_state, config=config)
        end_time = datetime.now()
        
        print(f"✅ Demo completed in {(end_time - start_time).total_seconds():.2f}s")
        print(f"📋 Result: {result.get('status', 'unknown')}")
        print(f"🔄 Retries: {result.get('retries', 0)}")
        print()
        print("🎯 Check LangStudio for complete interactive visualization!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    # Setup enterprise visualization
    setup_enterprise_visualization()
    
    # Run demo workflow
    asyncio.run(demonstrate_interactive_workflow())