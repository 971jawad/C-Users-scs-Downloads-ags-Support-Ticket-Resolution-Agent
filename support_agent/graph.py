"""
LangGraph Support Agent Graph Definition
This module defines the complete support ticket resolution workflow using LangGraph.

The graph implements a multi-step process:
1. Ticket Classification
2. Context Retrieval (RAG)
3. Response Generation
4. Quality Review
5. Retry Logic (max 2 attempts)
6. Escalation Handling

Architecture follows LangGraph best practices with modular nodes,
proper state management, and production-ready error handling.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, Literal
import logging
import os

# LangSmith integration for enterprise-level monitoring
try:
    from langsmith import Client
    from langsmith.run_helpers import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

from support_agent.state import SupportTicketState
from support_agent.nodes import (
    classify_ticket_node,
    retrieve_context_node,
    generate_response_node,
    review_response_node,
    refine_context_node,
    escalate_ticket_node,
    finalize_response_node
)

logger = logging.getLogger(__name__)

def create_support_agent_graph():
    """
    Create and compile the LangGraph support agent workflow with enterprise-level monitoring.
    
    This function defines the complete graph structure with all nodes and edges,
    implementing the exact workflow specified in the assessment task:
    - Multi-step orchestration with conditional routing
    - Retry logic with maximum 2 attempts
    - Escalation handling for failed cases
    - State persistence and checkpointing
    - LangSmith integration for interactive visualization
    
    Returns:
        Compiled LangGraph instance ready for execution with LangStudio integration
    """
    logger.info("Creating support agent graph with LangSmith integration...")
    
    # Configure LangSmith for interactive workflow visualization
    if LANGSMITH_AVAILABLE:
        # Clear any conflicting session variables first
        problematic_vars = ["REPLIT_SESSION", "LANGCHAIN_SESSION", "SESSION_ID"]
        for var in problematic_vars:
            if var in os.environ:
                del os.environ[var]
                
        # Enable LangSmith tracing for interactive LangStudio visualization
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "Support-Ticket-Resolution-Agent"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        
        # Initialize LangSmith client for enterprise monitoring
        try:
            langsmith_client = Client()
            logger.info("LangSmith client initialized for interactive workflow visualization")
            logger.info(f"Project set to: {os.environ.get('LANGCHAIN_PROJECT')}")
            logger.info(f"Tracing enabled: {os.environ.get('LANGCHAIN_TRACING_V2')}")
        except Exception as e:
            logger.warning(f"LangSmith client initialization failed: {e}")
            langsmith_client = None
    else:
        langsmith_client = None
    
    # Initialize the state graph with our custom state schema
    workflow = StateGraph(SupportTicketState)
    
    # Add all processing nodes to the graph
    # Each node is a specialized function handling one aspect of ticket processing
    
    # 1. Classification Node - Determines ticket category
    workflow.add_node("classify_ticket", classify_ticket_node)
    
    # 2. Context Retrieval Node - RAG-based context fetching
    workflow.add_node("retrieve_context", retrieve_context_node)
    
    # 3. Response Generation Node - Draft response creation
    workflow.add_node("generate_response", generate_response_node)
    
    # 4. Review Node - Quality and policy compliance check
    workflow.add_node("review_response", review_response_node)
    
    # 5. Context Refinement Node - Retry with improved context
    workflow.add_node("refine_context", refine_context_node)
    
    # 6. Escalation Node - Handle failed cases
    workflow.add_node("escalate_ticket", escalate_ticket_node)
    
    # 7. Finalization Node - Prepare final response
    workflow.add_node("finalize_response", finalize_response_node)
    
    # Define the workflow edges and routing logic
    
    # Entry point: Start with ticket classification
    workflow.set_entry_point("classify_ticket")
    
    # Classification -> Context Retrieval (always follows classification)
    workflow.add_edge("classify_ticket", "retrieve_context")
    
    # Context Retrieval -> Response Generation (always follows retrieval)
    workflow.add_edge("retrieve_context", "generate_response")
    
    # Response Generation -> Review (always review generated responses)
    workflow.add_edge("generate_response", "review_response")
    
    # Review -> Conditional routing based on review outcome
    def review_routing(state: SupportTicketState) -> Literal["finalize_response", "refine_context", "escalate_ticket"]:
        """
        Route based on review results and retry count.
        
        This function implements the core retry logic:
        - If review passes: proceed to finalization
        - If review fails and retries < 2: attempt refinement
        - If review fails and retries >= 2: escalate to human
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name to execute
        """
        logger.info(f"Review routing - Retries: {state['retries']}, Status: {state.get('review_status', 'unknown')}")
        
        # Check if the last review passed
        review_status = state.get('review_status', 'failed')
        
        if review_status == 'approved':
            logger.info("Review approved - proceeding to finalization")
            return "finalize_response"
        
        # Review failed - check retry count
        if state['retries'] < 2:
            logger.info(f"Review failed - attempting retry {state['retries'] + 1}")
            return "refine_context"
        else:
            logger.info("Review failed - maximum retries reached, escalating")
            return "escalate_ticket"
    
    # Add conditional edge from review node
    workflow.add_conditional_edges(
        "review_response",
        review_routing,
        {
            "finalize_response": "finalize_response",
            "refine_context": "refine_context", 
            "escalate_ticket": "escalate_ticket"
        }
    )
    
    # Context refinement -> increment retry counter and generate new response
    def increment_retry_and_generate(state: SupportTicketState) -> SupportTicketState:
        """Increment retry counter before generating new response."""
        state['retries'] += 1
        return state
    
    workflow.add_edge("refine_context", "generate_response")
    
    # Terminal nodes - both end the workflow
    workflow.add_edge("finalize_response", END)
    workflow.add_edge("escalate_ticket", END)
    
    # Add memory checkpointing for debugging and state persistence
    memory = MemorySaver()
    
    # Compile the graph with checkpointing and LangSmith integration
    compiled_graph = workflow.compile(
        checkpointer=memory,
        # Enable LangSmith tracing for enterprise-level monitoring
        debug=True if LANGSMITH_AVAILABLE else False
    )
    
    # Add metadata for LangStudio visualization
    if LANGSMITH_AVAILABLE and langsmith_client:
        # Store metadata for later reference instead of assigning to config
        compiled_graph._langsmith_metadata = {
            "project_name": "Support-Ticket-Resolution-Agent",
            "description": "Enterprise AI Support Ticket Resolution System",
            "version": "1.0.0",
            "workflow_type": "support_ticket_resolution",
            "monitoring_enabled": True
        }
    
    logger.info("Support agent graph compiled successfully with LangSmith integration")
    return compiled_graph

def visualize_graph():
    """
    Generate a visual representation of the support agent graph.
    Useful for debugging and documentation purposes.
    
    Returns:
        Graph visualization data for LangGraph Studio
    """
    try:
        graph = create_support_agent_graph()
        
        # Generate mermaid diagram representation
        mermaid_graph = graph.get_graph().print_ascii()
        logger.info("Graph visualization generated")
        
        return mermaid_graph
        
    except Exception as e:
        logger.error(f"Error generating graph visualization: {str(e)}")
        return None

# Graph configuration for LangGraph CLI
def get_graph_config() -> Dict[str, Any]:
    """
    Return configuration for the LangGraph CLI.
    This enables proper integration with LangGraph Studio and debugging tools.
    
    Returns:
        Dictionary containing graph configuration
    """
    return {
        "graph_id": "support_agent",
        "title": "Support Ticket Resolution Agent",
        "description": "Multi-step support ticket resolution with retry logic and escalation",
        "version": "1.0.0",
        "nodes": [
            "classify_ticket",
            "retrieve_context", 
            "generate_response",
            "review_response",
            "refine_context",
            "escalate_ticket",
            "finalize_response"
        ],
        "entry_point": "classify_ticket",
        "terminal_nodes": ["finalize_response", "escalate_ticket"]
    }

if __name__ == "__main__":
    # Test graph creation and visualization
    print("Creating support agent graph...")
    graph = create_support_agent_graph()
    print("Graph created successfully!")
    
    # Print graph structure
    print("\nGraph Structure:")
    print(visualize_graph())
