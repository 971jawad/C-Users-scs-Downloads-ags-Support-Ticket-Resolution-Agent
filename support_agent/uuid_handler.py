"""
UUID Handler for LangSmith Integration

Handles UUID generation and validation for LangStudio workflow visualization
while avoiding conflicts with Replit environment variables.
"""

import uuid
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_clean_thread_id() -> str:
    """
    Generate a clean UUID for LangSmith thread identification.
    
    Ensures proper UUID format that passes LangSmith validation
    while avoiding conflicts with Replit session variables.
    
    Returns:
        str: Valid UUID string for LangSmith thread_id
    """
    # Generate a clean UUID v4
    thread_id = str(uuid.uuid4())
    logger.info(f"Generated clean thread ID: {thread_id}")
    return thread_id

def create_langsmith_config(thread_id: str) -> Dict[str, Any]:
    """
    Create LangSmith configuration with proper thread ID.
    
    Args:
        thread_id: Valid UUID string for the workflow execution
        
    Returns:
        Dict containing LangSmith configuration
    """
    # Temporarily clear any problematic environment variables
    original_session = os.environ.get("REPLIT_SESSION")
    if "REPLIT_SESSION" in os.environ:
        del os.environ["REPLIT_SESSION"]
    
    config = {
        "configurable": {
            "thread_id": thread_id
        },
        "metadata": {
            "project": "Support-Ticket-Resolution-Agent",
            "workflow_type": "support_ticket_resolution",
            "environment": "replit"
        }
    }
    
    # Restore the original session variable
    if original_session:
        os.environ["REPLIT_SESSION"] = original_session
    
    logger.info(f"Created LangSmith config with thread_id: {thread_id}")
    return config

def get_langstudio_url(thread_id: str) -> str:
    """
    Generate LangStudio URL for interactive workflow visualization.
    
    Args:
        thread_id: Valid UUID string for the execution trace
        
    Returns:
        str: Complete LangStudio URL for interactive monitoring
    """
    base_url = "https://smith.langchain.com/o/1acbd1a3-5fab-4e23-8d1b-5dc5c014d2c3/projects/p/Support-Ticket-Resolution-Agent/r"
    studio_url = f"{base_url}/{thread_id}"
    
    logger.info(f"Generated LangStudio URL: {studio_url}")
    return studio_url

def validate_uuid_format(uuid_string: str) -> bool:
    """
    Validate UUID format for LangSmith compatibility.
    
    Args:
        uuid_string: String to validate as UUID
        
    Returns:
        bool: True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        logger.error(f"Invalid UUID format: {uuid_string}")
        return False