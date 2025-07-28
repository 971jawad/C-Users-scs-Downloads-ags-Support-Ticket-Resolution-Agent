"""
Langfuse Configuration for AI Agent Workflow Visualization

This module configures Langfuse integration to provide interactive workflow visualization
for real-time monitoring of support ticket processing with enhanced tracing.
"""

import os
import logging
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

def setup_langfuse_monitoring() -> bool:
    """
    Configure Langfuse for AI agent workflow monitoring and visualization.
    
    Returns:
        True if Langfuse is properly configured, False otherwise
    """
    try:
        # Check if API keys are available
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not public_key or not secret_key:
            logger.warning("Langfuse API keys not found. Interactive visualization will be limited.")
            return False
        
        # Test Langfuse connection
        try:
            from langfuse import Langfuse
            client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )
            # Test connection
            client.auth_check()
            logger.info("Langfuse client connected successfully")
        except Exception as client_error:
            logger.error(f"Langfuse client connection failed: {client_error}")
            return False
        
        logger.info("Langfuse monitoring configured successfully for interactive workflow visualization")
        logger.info(f"Interactive workflow visualization available at: {host}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure Langfuse monitoring: {str(e)}")
        return False

def get_langfuse_url(trace_id: Optional[str] = None) -> str:
    """
    Generate Langfuse URL for interactive workflow visualization.
    
    Args:
        trace_id: Optional trace ID for specific execution trace
        
    Returns:
        Complete Langfuse URL for workflow visualization
    """
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if trace_id:
        return f"{host}/trace/{trace_id}"
    else:
        return f"{host}/project/default"

def create_workflow_metadata() -> Dict[str, Any]:
    """
    Create metadata for enhanced Langfuse visualization.
    
    Returns:
        Metadata dictionary for workflow tracing
    """
    return {
        "workflow_name": "Support Ticket Resolution Agent",
        "workflow_type": "multi_step_llm_workflow",
        "framework": "LangGraph",
        "llm_provider": "Google Gemini 2.0 Flash",
        "rag_system": "FAISS + BGE Embeddings",
        "retry_logic": "max_2_attempts",
        "escalation": "csv_logging",
        "monitoring_level": "enterprise",
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
        "conditional_routing": ["review_routing"],
        "terminal_nodes": ["finalize_response", "escalate_ticket"]
    }

def log_workflow_execution(state: Dict[str, Any], node_name: str, execution_time: float) -> None:
    """
    Log workflow execution details for Langfuse visualization.
    
    Args:
        state: Current workflow state
        node_name: Name of the executing node
        execution_time: Time taken to execute the node
    """
    try:
        metadata = {
            "node": node_name,
            "execution_time_seconds": execution_time,
            "ticket_category": state.get('category', 'unknown'),
            "retry_count": state.get('retries', 0),
            "escalated": state.get('escalated', False),
            "status": state.get('status', 'unknown')
        }
        
        logger.info(f"Node execution logged: {node_name}", extra={"metadata": metadata})
        
    except Exception as e:
        logger.warning(f"Failed to log workflow execution: {str(e)}")

def create_langfuse_trace(ticket_data: Dict[str, Any]) -> str:
    """
    Create a new Langfuse trace for ticket processing.
    
    Args:
        ticket_data: Ticket information
        
    Returns:
        Trace ID for the workflow execution
    """
    try:
        from langfuse import Langfuse
        
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not public_key or not secret_key:
            return str(uuid.uuid4())
        
        client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        
        trace_id = str(uuid.uuid4())
        
        trace = client.trace(
            id=trace_id,
            name="Support Ticket Processing",
            metadata={
                "ticket_subject": ticket_data.get("subject", ""),
                "category": ticket_data.get("category", "unknown"),
                "timestamp": ticket_data.get("timestamp", ""),
                **create_workflow_metadata()
            }
        )
        
        return trace_id
        
    except Exception as e:
        logger.error(f"Failed to create Langfuse trace: {str(e)}")
        return str(uuid.uuid4())

def is_langfuse_enabled() -> bool:
    """Check if Langfuse monitoring is properly configured."""
    try:
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        return bool(public_key and secret_key)
    except:
        return False

# Initialize Langfuse on module import
_langfuse_enabled = setup_langfuse_monitoring()