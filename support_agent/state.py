"""
Support Ticket State Schema for LangGraph

This module defines the state structure used throughout the support ticket
resolution workflow. The state maintains all necessary information across
nodes and provides type safety for the entire graph execution.

Following LangGraph best practices for state management:
- Comprehensive but minimal state structure
- Type hints for clarity and safety
- Immutable design with proper updates
- Clear documentation for each field
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime

class TicketInfo(TypedDict):
    """
    Structure for the original support ticket information.
    
    This represents the input from the user that initiates the workflow.
    """
    subject: str        # Brief description of the issue
    description: str    # Detailed explanation of the problem

class ContextDocument(TypedDict):
    """
    Structure for retrieved context documents from RAG system.
    
    Each document contains the content and metadata for response generation.
    """
    content: str                    # The actual document content
    source: str                     # Source identifier (filename, URL, etc.)
    relevance_score: float         # Similarity score from vector search
    category: str                  # Document category for filtering

class ReviewFeedback(TypedDict):
    """
    Structure for review feedback from the quality assurance node.
    
    Captures the review decision and specific feedback for improvements.
    """
    status: Literal['approved', 'rejected']  # Review decision
    feedback: str                            # Specific feedback text
    timestamp: str                           # When the review was conducted
    attempt: int                            # Which attempt this review is for

class SupportTicketState(TypedDict):
    """
    Complete state structure for the support ticket resolution workflow.
    
    This state is passed between all nodes in the LangGraph and maintains
    the complete context of ticket processing. Each field serves a specific
    purpose in the workflow:
    
    Core Data:
    - ticket: Original user input
    - category: Classified ticket category
    - retrieved_context: RAG-retrieved documents
    - drafts: All generated response attempts
    - review_feedback: All review results
    - final_output: The final response or escalation message
    
    Processing Control:
    - retries: Number of retry attempts made
    - status: Current processing status
    - escalated: Whether ticket was escalated to human
    - review_status: Latest review result
    - latest_feedback: Most recent review feedback
    - current_draft: The current response being processed
    
    State Management:
    - All fields are typed for safety
    - State is updated incrementally by nodes
    - Complete history is preserved for debugging
    - Supports both successful resolution and escalation paths
    """
    
    # Original ticket information (immutable)
    ticket: TicketInfo
    
    # Classification result
    category: str  # One of: Billing, Technical, Security, General
    
    # RAG retrieval results
    retrieved_context: List[ContextDocument]
    
    # Response generation history
    drafts: List[str]           # All generated response drafts
    current_draft: Optional[str] # Currently active draft being processed
    
    # Review and feedback system
    review_feedback: List[ReviewFeedback]  # Complete review history
    review_status: Optional[str]           # Latest review status
    latest_feedback: Optional[str]         # Most recent feedback text
    
    # Final output
    final_output: str           # Final response or escalation message
    
    # Processing control
    retries: int               # Number of retry attempts (max 2)
    status: str               # Current workflow status
    escalated: bool           # Whether ticket was escalated
    
    # Optional metadata
    processing_start_time: Optional[str]    # Workflow start timestamp
    processing_end_time: Optional[str]      # Workflow completion timestamp
    node_execution_log: Optional[List[str]] # Log of node executions

# Status constants for workflow tracking
class WorkflowStatus:
    """
    Standard status values used throughout the workflow.
    
    These constants ensure consistency in status tracking and
    enable proper conditional routing in the graph.
    """
    INITIALIZED = "initialized"        # Initial state
    CLASSIFIED = "classified"          # After ticket classification
    CONTEXT_RETRIEVED = "context_retrieved"  # After RAG retrieval
    RESPONSE_GENERATED = "response_generated"  # After draft generation
    REVIEWED = "reviewed"              # After quality review
    CONTEXT_REFINED = "context_refined"  # After retry context update
    RESOLVED = "resolved"              # Successfully completed
    ESCALATED = "escalated"            # Escalated to human
    ERROR = "error"                    # Error occurred

# Category constants for classification
class TicketCategory:
    """
    Standard ticket categories supported by the system.
    
    These categories determine which RAG knowledge base is queried
    and influence response generation prompts.
    """
    BILLING = "Billing"
    TECHNICAL = "Technical"
    SECURITY = "Security"
    GENERAL = "General"

def create_initial_state(ticket: Dict[str, str]) -> SupportTicketState:
    """
    Create a new initial state for ticket processing.
    
    This function initializes all state fields with appropriate default
    values, ensuring the state is ready for graph execution.
    
    Args:
        ticket: Dictionary with 'subject' and 'description' keys
        
    Returns:
        Initialized SupportTicketState ready for processing
    """
    return SupportTicketState(
        # Core ticket data
        ticket=TicketInfo(
            subject=ticket['subject'],
            description=ticket['description']
        ),
        
        # Processing results (empty initially)
        category="",
        retrieved_context=[],
        drafts=[],
        current_draft=None,
        review_feedback=[],
        review_status=None,
        latest_feedback=None,
        final_output="",
        
        # Control fields
        retries=0,
        status=WorkflowStatus.INITIALIZED,
        escalated=False,
        
        # Metadata
        processing_start_time=datetime.now().isoformat(),
        processing_end_time=None,
        node_execution_log=[]
    )

def validate_state(state: SupportTicketState) -> bool:
    """
    Validate that the state contains all required fields and valid data.
    
    This function performs comprehensive validation to ensure state integrity
    throughout the workflow execution.
    
    Args:
        state: State to validate
        
    Returns:
        True if state is valid, False otherwise
    """
    try:
        # Check required fields exist
        required_fields = ['ticket', 'category', 'retrieved_context', 'drafts', 
                          'review_feedback', 'final_output', 'retries', 'status', 'escalated']
        
        for field in required_fields:
            if field not in state:
                return False
        
        # Validate ticket structure
        if not isinstance(state['ticket'], dict):
            return False
        
        if 'subject' not in state['ticket'] or 'description' not in state['ticket']:
            return False
        
        # Validate types
        if not isinstance(state['retries'], int) or state['retries'] < 0:
            return False
        
        if not isinstance(state['escalated'], bool):
            return False
        
        if not isinstance(state['drafts'], list):
            return False
        
        if not isinstance(state['review_feedback'], list):
            return False
        
        return True
        
    except Exception:
        return False

def log_state_transition(state: SupportTicketState, node_name: str, action: str) -> SupportTicketState:
    """
    Log a state transition for debugging and monitoring.
    
    This function adds an entry to the node execution log, helping with
    workflow debugging and performance monitoring.
    
    Args:
        state: Current state
        node_name: Name of the executing node
        action: Description of the action taken
        
    Returns:
        Updated state with log entry added
    """
    if 'node_execution_log' not in state or state['node_execution_log'] is None:
        state['node_execution_log'] = []
    
    log_entry = f"{datetime.now().isoformat()} - {node_name}: {action}"
    if state['node_execution_log'] is not None:
        state['node_execution_log'].append(log_entry)
    
    return state

# Export commonly used types and functions
__all__ = [
    'SupportTicketState',
    'TicketInfo',
    'ContextDocument', 
    'ReviewFeedback',
    'WorkflowStatus',
    'TicketCategory',
    'create_initial_state',
    'validate_state',
    'log_state_transition'
]
