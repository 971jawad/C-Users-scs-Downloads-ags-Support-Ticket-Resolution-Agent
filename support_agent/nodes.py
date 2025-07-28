"""
LangGraph Node Functions for Support Agent

This module implements all the processing nodes for the support ticket
resolution workflow. Each node performs a specific step in the pipeline
and updates the state accordingly.
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

from support_agent.state import SupportTicketState, ReviewFeedback, log_state_transition
from support_agent.gemini_client import GeminiClient  
from support_agent.rag_system import RAGSystem
from support_agent.utils import save_escalation_log

logger = logging.getLogger(__name__)

# Initialize shared components
gemini_client = None
rag_system = None

def initialize_components():
    """Initialize shared components for all nodes."""
    global gemini_client, rag_system
    try:
        gemini_client = GeminiClient()
        rag_system = RAGSystem()
        logger.info("Node components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

# Initialize on module load
try:
    initialize_components()
except Exception as e:
    logger.warning(f"Component initialization failed: {e}")

async def classify_ticket_node(state: SupportTicketState) -> SupportTicketState:
    """
    Classify the support ticket into one of four categories.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with classification result
    """
    try:
        logger.info("Starting ticket classification")
        
        ticket = state['ticket']
        subject = ticket['subject']
        description = ticket['description']
        
        # Classify using Gemini
        if gemini_client:
            category = await gemini_client.classify_ticket(subject, description)
        else:
            # Fallback classification if Gemini unavailable
            category = _fallback_classify(subject, description)
        
        # Update state
        state['category'] = category
        state['status'] = 'classified'
        
        logger.info(f"Ticket classified as: {category}")
        return log_state_transition(state, "classify_ticket", f"Classified as {category}")
        
    except Exception as e:
        logger.error(f"Error in ticket classification: {str(e)}")
        state['category'] = 'General'
        state['status'] = 'classified'
        return log_state_transition(state, "classify_ticket", f"Error occurred, defaulted to General")

async def retrieve_context_node(state: SupportTicketState) -> SupportTicketState:
    """
    Retrieve relevant context documents using RAG system.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with retrieved context
    """
    try:
        logger.info("Starting context retrieval")
        
        ticket = state['ticket']
        category = state['category']
        
        # Enhance query for better retrieval
        if rag_system:
            query = rag_system.enhance_query(ticket['subject'], ticket['description'])
            context_docs = await rag_system.retrieve_context(
                query=query,
                category=category,
                top_k=3,
                include_related=True
            )
        else:
            context_docs = []
        
        # Update state
        state['retrieved_context'] = context_docs
        state['status'] = 'context_retrieved'
        
        logger.info(f"Retrieved {len(context_docs)} context documents")
        return log_state_transition(state, "retrieve_context", f"Retrieved {len(context_docs)} documents")
        
    except Exception as e:
        logger.error(f"Error in context retrieval: {str(e)}")
        state['retrieved_context'] = []
        state['status'] = 'context_retrieved'
        return log_state_transition(state, "retrieve_context", "Error occurred, proceeding without context")

async def generate_response_node(state: SupportTicketState) -> SupportTicketState:
    """
    Generate a support response using Gemini and retrieved context.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated response
    """
    try:
        logger.info("Starting response generation")
        
        ticket = state['ticket']
        category = state['category']
        context_docs = state['retrieved_context']
        
        # Get previous feedback if this is a retry
        previous_feedback = None
        if state['review_feedback']:
            latest_review = state['review_feedback'][-1]
            if latest_review['status'] == 'rejected':
                previous_feedback = latest_review['feedback']
        
        # Generate intelligent, contextual response
        if gemini_client:
            # Import advanced response generation functions
            from support_agent.intelligent_response import (
                analyze_user_profile, analyze_context_relevance, 
                assess_issue_complexity, enhance_response_with_context
            )
            
            # Perform advanced analysis
            user_profile = analyze_user_profile(ticket)
            context_analysis = analyze_context_relevance(context_docs, ticket)
            issue_complexity = assess_issue_complexity(ticket, category)
            
            # Generate with advanced prompting
            response = await gemini_client.generate_intelligent_response(
                ticket_subject=ticket['subject'],
                ticket_description=ticket['description'],
                category=category,
                context_documents=context_docs,
                user_profile=user_profile,
                context_analysis=context_analysis,
                issue_complexity=issue_complexity,
                previous_feedback=previous_feedback
            )
            
            # Enhance response with contextual information
            response = enhance_response_with_context(response, user_profile, context_analysis)
        else:
            response = _fallback_response(ticket, category, context_docs)
        
        # Update state
        state['drafts'].append(response)
        state['current_draft'] = response
        state['status'] = 'response_generated'
        
        logger.info(f"Generated response of {len(response)} characters")
        return log_state_transition(state, "generate_response", "Response generated successfully")
        
    except Exception as e:
        logger.error(f"Error in response generation: {str(e)}")
        fallback_response = f"I apologize, but I'm experiencing technical difficulties. Please contact our support team directly for assistance with your {state.get('category', 'support').lower()} inquiry."
        state['drafts'].append(fallback_response)
        state['current_draft'] = fallback_response
        state['status'] = 'response_generated'
        return log_state_transition(state, "generate_response", "Error occurred, generated fallback response")

async def review_response_node(state: SupportTicketState) -> SupportTicketState:
    """
    Review the generated response for quality and policy compliance.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with review feedback
    """
    try:
        logger.info("Starting response review")
        
        ticket = state['ticket']
        current_response = state['current_draft']
        context_docs = state['retrieved_context']
        
        # Review response
        if gemini_client and current_response:
            review_result = await gemini_client.review_response(
                ticket_subject=ticket['subject'],
                ticket_description=ticket['description'],
                generated_response=current_response,
                context_documents=context_docs
            )
        else:
            # Simple fallback review
            review_result = {
                "status": "approved",
                "feedback": "Automated review completed"
            }
        
        # Create review feedback entry
        review_feedback = ReviewFeedback(
            status=review_result['status'],
            feedback=review_result['feedback'],
            timestamp=datetime.now().isoformat(),
            attempt=len(state['review_feedback']) + 1
        )
        
        # Update state
        state['review_feedback'].append(review_feedback)
        state['review_status'] = review_result['status']
        state['latest_feedback'] = review_result['feedback']
        state['status'] = 'reviewed'
        
        logger.info(f"Review completed: {review_result['status']}")
        return log_state_transition(state, "review_response", f"Review: {review_result['status']}")
        
    except Exception as e:
        logger.error(f"Error in response review: {str(e)}")
        # Default to approved on error
        fallback_review = ReviewFeedback(
            status='approved',
            feedback='Review system unavailable, proceeding with response',
            timestamp=datetime.now().isoformat(),
            attempt=len(state['review_feedback']) + 1
        )
        state['review_feedback'].append(fallback_review)
        state['review_status'] = 'approved'
        state['latest_feedback'] = fallback_review['feedback']
        state['status'] = 'reviewed'
        return log_state_transition(state, "review_response", "Error occurred, defaulted to approved")

async def refine_context_node(state: SupportTicketState) -> SupportTicketState:
    """
    Refine context retrieval based on review feedback.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with refined context
    """
    try:
        logger.info("Starting context refinement")
        
        ticket = state['ticket']
        category = state['category']
        feedback = state['latest_feedback']
        
        # Create enhanced query incorporating feedback
        enhanced_query = f"{ticket['subject']} {ticket['description']} {feedback}"
        
        if rag_system:
            # Retrieve with broader search
            refined_context = await rag_system.retrieve_context(
                query=enhanced_query,
                category=category,
                top_k=5,  # Get more documents
                include_related=True,
                min_relevance=0.05  # Lower threshold
            )
        else:
            refined_context = state['retrieved_context']
        
        # Update state
        state['retrieved_context'] = refined_context
        state['status'] = 'context_refined'
        
        logger.info(f"Context refined: {len(refined_context)} documents")
        return log_state_transition(state, "refine_context", f"Refined to {len(refined_context)} documents")
        
    except Exception as e:
        logger.error(f"Error in context refinement: {str(e)}")
        state['status'] = 'context_refined'
        return log_state_transition(state, "refine_context", "Error occurred, keeping existing context")

async def escalate_ticket_node(state: SupportTicketState) -> SupportTicketState:
    """
    Escalate ticket to human agent when automated resolution fails.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with escalation details
    """
    try:
        logger.info("Starting ticket escalation")
        
        # Create escalation message
        escalation_message = (
            "This ticket has been escalated to our human support team for personalized assistance. "
            "A support specialist will review your case and provide a detailed response within our "
            "standard response time. Thank you for your patience."
        )
        
        # Save escalation log
        escalation_data = {
            'timestamp': datetime.now().isoformat(),
            'ticket_subject': state['ticket']['subject'],
            'ticket_description': state['ticket']['description'],
            'category': state['category'],
            'retries': state['retries'],
            'review_feedback': state['review_feedback'],
            'final_drafts': state['drafts']
        }
        
        save_escalation_log(escalation_data)
        
        # Update state
        state['final_output'] = escalation_message
        state['escalated'] = True
        state['status'] = 'escalated'
        
        logger.info("Ticket escalated successfully")
        return log_state_transition(state, "escalate_ticket", "Ticket escalated to human agent")
        
    except Exception as e:
        logger.error(f"Error in ticket escalation: {str(e)}")
        state['final_output'] = "Your ticket has been forwarded to our support team."
        state['escalated'] = True
        state['status'] = 'escalated'
        return log_state_transition(state, "escalate_ticket", "Error occurred during escalation")

async def finalize_response_node(state: SupportTicketState) -> SupportTicketState:
    """
    Finalize the approved response and complete the workflow.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with finalized response
    """
    try:
        logger.info("Finalizing response")
        
        # Set final output to the approved response
        state['final_output'] = state['current_draft']
        state['status'] = 'resolved'
        state['processing_end_time'] = datetime.now().isoformat()
        
        logger.info("Response finalized successfully")
        return log_state_transition(state, "finalize_response", "Workflow completed successfully")
        
    except Exception as e:
        logger.error(f"Error in response finalization: {str(e)}")
        state['final_output'] = state.get('current_draft', 'Response processing completed.')
        state['status'] = 'resolved'
        state['processing_end_time'] = datetime.now().isoformat()
        return log_state_transition(state, "finalize_response", "Error occurred during finalization")

# Utility functions for fallback behavior

def _fallback_classify(subject: str, description: str) -> str:
    """Simple keyword-based classification fallback."""
    text = f"{subject} {description}".lower()
    
    if any(word in text for word in ['bill', 'payment', 'charge', 'refund', 'price']):
        return 'Billing'
    elif any(word in text for word in ['api', 'error', 'bug', 'technical', 'integration']):
        return 'Technical'
    elif any(word in text for word in ['security', 'password', 'login', 'access', 'authentication']):
        return 'Security'
    else:
        return 'General'

def _fallback_response(ticket: Dict[str, str], category: str, context_docs: list) -> str:
    """Generate a simple fallback response when Gemini is unavailable."""
    return f"""Thank you for contacting our {category.lower()} support team.

We have received your inquiry regarding: {ticket['subject']}

Our team is currently reviewing your request and will provide a detailed response within our standard response time. 

If this is an urgent matter, please contact our priority support line.

Best regards,
Support Team"""