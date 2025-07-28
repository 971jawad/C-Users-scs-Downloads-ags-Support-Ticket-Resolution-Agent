"""
Intelligent Response Generation System

This module implements advanced AI-driven response generation with:
- Contextual analysis and synthesis
- User profiling and personalization
- Sentiment and urgency detection
- Dynamic solution adaptation
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def analyze_user_profile(ticket: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze user profile from ticket content to personalize response.
    
    Args:
        ticket: Dictionary containing subject and description
        
    Returns:
        User profile with personalization factors
    """
    subject = ticket['subject'].lower()
    description = ticket['description'].lower()
    combined_text = f"{subject} {description}"
    
    # Sentiment analysis
    negative_indicators = ['cant', 'cannot', 'broken', 'failed', 'error', 'issue', 'problem', 'frustrated', 'urgent', 'immediately']
    positive_indicators = ['please', 'thank', 'help', 'could', 'would']
    
    negative_count = sum(1 for word in negative_indicators if word in combined_text)
    positive_count = sum(1 for word in positive_indicators if word in combined_text)
    
    if negative_count > positive_count + 1:
        sentiment = "frustrated"
        preferred_tone = "empathetic and solution-focused"
    elif positive_count > negative_count:
        sentiment = "polite"
        preferred_tone = "friendly and helpful"
    else:
        sentiment = "neutral"
        preferred_tone = "professional and direct"
    
    # Technical level assessment
    technical_keywords = ['api', 'database', 'server', 'configuration', 'authentication', 'integration', 'sdk', 'webhook']
    basic_keywords = ['login', 'password', 'email', 'account', 'profile', 'settings']
    
    technical_count = sum(1 for word in technical_keywords if word in combined_text)
    basic_count = sum(1 for word in basic_keywords if word in combined_text)
    
    if technical_count > 2:
        technical_level = "advanced"
        personalization_level = "technical"
    elif basic_count > technical_count:
        technical_level = "basic"
        personalization_level = "simple"
    else:
        technical_level = "intermediate"
        personalization_level = "balanced"
    
    # Urgency detection
    urgency_keywords = ['urgent', 'immediately', 'asap', 'critical', 'emergency', 'production', 'down', 'broken']
    urgency_count = sum(1 for word in urgency_keywords if word in combined_text)
    
    if urgency_count > 0 or 'urgent' in subject or 'critical' in subject:
        urgency = "high"
    elif any(word in combined_text for word in ['soon', 'quick', 'fast']):
        urgency = "medium"
    else:
        urgency = "low"
    
    # User type inference
    if technical_count > 1:
        user_type = "developer"
    elif any(word in combined_text for word in ['business', 'company', 'team', 'organization']):
        user_type = "business_user"
    else:
        user_type = "end_user"
    
    return {
        'sentiment': sentiment,
        'technical_level': technical_level,
        'urgency': urgency,
        'user_type': user_type,
        'preferred_tone': preferred_tone,
        'personalization_level': personalization_level,
        'response_style': determine_response_style(sentiment, technical_level, urgency)
    }

def determine_response_style(sentiment: str, technical_level: str, urgency: str) -> str:
    """Determine the optimal response style based on user profile."""
    if urgency == "high":
        if technical_level == "advanced":
            return "direct_technical_immediate"
        else:
            return "empathetic_immediate_simple"
    elif sentiment == "frustrated":
        return "empathetic_solution_focused"
    elif technical_level == "advanced":
        return "detailed_technical"
    else:
        return "friendly_comprehensive"

def analyze_context_relevance(context_docs: List[Dict], ticket: Dict[str, str]) -> Dict[str, Any]:
    """
    Perform intelligent analysis of context relevance and synthesize knowledge.
    
    Args:
        context_docs: List of retrieved context documents
        ticket: Original ticket information
        
    Returns:
        Analyzed and synthesized context information
    """
    if not context_docs:
        return {
            'synthesized_knowledge': "No specific policy documentation found for this issue.",
            'confidence_level': "low",
            'key_concepts': [],
            'action_items': []
        }
    
    # Extract key concepts from ticket
    ticket_text = f"{ticket['subject']} {ticket['description']}".lower()
    
    # Analyze document relevance and extract key information
    relevant_docs = []
    key_concepts = set()
    action_items = []
    
    for doc in context_docs:
        content = doc['content'].lower()
        relevance_score = doc.get('relevance_score', 0)
        
        if relevance_score > 0.1:  # Only include reasonably relevant docs
            relevant_docs.append(doc)
            
            # Extract action-oriented content
            if any(word in content for word in ['step', 'follow', 'click', 'navigate', 'contact', 'submit']):
                action_items.append(doc['content'])
            
            # Extract key concepts
            concepts = extract_key_concepts(content)
            key_concepts.update(concepts)
    
    # Synthesize knowledge into coherent guidance
    synthesized_knowledge = synthesize_documents(relevant_docs, ticket_text)
    
    confidence_level = "high" if len(relevant_docs) >= 2 else "medium" if relevant_docs else "low"
    
    return {
        'synthesized_knowledge': synthesized_knowledge,
        'confidence_level': confidence_level,
        'key_concepts': list(key_concepts),
        'action_items': action_items,
        'relevant_document_count': len(relevant_docs)
    }

def extract_key_concepts(content: str) -> List[str]:
    """Extract key concepts from document content."""
    # Simple keyword extraction - could be enhanced with NLP
    key_patterns = [
        r'required?\s+to\s+(\w+(?:\s+\w+){0,2})',
        r'must\s+(\w+(?:\s+\w+){0,2})',
        r'should\s+(\w+(?:\s+\w+){0,2})',
        r'need\s+to\s+(\w+(?:\s+\w+){0,2})'
    ]
    
    concepts = []
    for pattern in key_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        concepts.extend(matches)
    
    return concepts[:5]  # Limit to top 5 concepts

def synthesize_documents(docs: List[Dict], ticket_context: str) -> str:
    """
    Synthesize multiple documents into coherent knowledge base.
    
    Args:
        docs: List of relevant documents
        ticket_context: Context from the original ticket
        
    Returns:
        Synthesized knowledge summary
    """
    if not docs:
        return "No relevant documentation found."
    
    # Group documents by type/source
    policy_docs = [doc for doc in docs if 'policy' in doc.get('source', '').lower()]
    procedure_docs = [doc for doc in docs if any(word in doc.get('source', '').lower() 
                                                for word in ['procedure', 'guide', 'steps'])]
    general_docs = [doc for doc in docs if doc not in policy_docs and doc not in procedure_docs]
    
    synthesis_parts = []
    
    if policy_docs:
        synthesis_parts.append("**Policy Guidelines:**")
        for doc in policy_docs[:2]:  # Limit to top 2 policy docs
            synthesis_parts.append(f"- {doc['content']}")
    
    if procedure_docs:
        synthesis_parts.append("**Procedures:**")
        for doc in procedure_docs[:2]:
            synthesis_parts.append(f"- {doc['content']}")
    
    if general_docs:
        synthesis_parts.append("**General Information:**")
        for doc in general_docs[:2]:
            synthesis_parts.append(f"- {doc['content']}")
    
    return "\n".join(synthesis_parts)

def assess_issue_complexity(ticket: Dict[str, str], category: str) -> Dict[str, Any]:
    """
    Assess the complexity level of the reported issue.
    
    Args:
        ticket: Ticket information
        category: Classified category
        
    Returns:
        Complexity assessment with recommended approach
    """
    subject = ticket['subject'].lower()
    description = ticket['description'].lower()
    combined_text = f"{subject} {description}"
    
    # Complexity indicators
    simple_indicators = ['password', 'login', 'forgot', 'reset', 'email', 'profile']
    moderate_indicators = ['setup', 'configuration', 'installation', 'integration', 'permission']
    complex_indicators = ['api', 'webhook', 'database', 'custom', 'advanced', 'development']
    
    simple_count = sum(1 for word in simple_indicators if word in combined_text)
    moderate_count = sum(1 for word in moderate_indicators if word in combined_text)
    complex_count = sum(1 for word in complex_indicators if word in combined_text)
    
    if complex_count > 0:
        level = "complex"
        reasoning = "Technical issue requiring detailed analysis"
        approach = "step_by_step_technical"
    elif moderate_count > simple_count:
        level = "moderate"
        reasoning = "Configuration or setup related issue"
        approach = "guided_resolution"
    else:
        level = "simple"
        reasoning = "Common user account or access issue"
        approach = "direct_solution"
    
    # Category-based complexity adjustment
    if category in ['Security', 'Technical']:
        if level == "simple":
            level = "moderate"
        elif level == "moderate":
            level = "complex"
    
    return {
        'level': level,
        'reasoning': reasoning,
        'recommended_approach': approach,
        'estimated_resolution_steps': get_estimated_steps(level)
    }

def get_estimated_steps(complexity_level: str) -> int:
    """Get estimated number of resolution steps based on complexity."""
    return {
        'simple': 2,
        'moderate': 4,
        'complex': 6
    }.get(complexity_level, 3)

def enhance_response_with_context(response: str, user_profile: Dict, context_analysis: Dict) -> str:
    """
    Enhance the generated response with contextual information and personalization.
    
    Args:
        response: Base generated response
        user_profile: User profile information
        context_analysis: Context analysis results
        
    Returns:
        Enhanced personalized response
    """
    enhancements = []
    
    # Add urgency acknowledgment if high priority
    if user_profile['urgency'] == 'high':
        enhancements.append("🚨 I understand this is urgent and I'm prioritizing your request.")
    
    # Add confidence indicator
    confidence = context_analysis['confidence_level']
    if confidence == 'high':
        enhancements.append("Based on our comprehensive policy documentation, here's what I can help you with:")
    elif confidence == 'medium':
        enhancements.append("I found some relevant information that should help:")
    else:
        enhancements.append("While I have limited specific documentation for this exact issue, I can provide general guidance:")
    
    # Combine base response with enhancements
    if enhancements:
        enhanced_response = f"{enhancements[0]}\n\n{response}"
        if len(enhancements) > 1:
            enhanced_response = f"{enhancements[1]}\n\n{enhanced_response}"
    else:
        enhanced_response = response
    
    # Add personalized closing based on user type
    closing = get_personalized_closing(user_profile)
    enhanced_response += f"\n\n{closing}"
    
    return enhanced_response

def get_personalized_closing(user_profile: Dict) -> str:
    """Generate personalized closing based on user profile."""
    if user_profile['user_type'] == 'developer':
        return "If you need additional API documentation or technical specifications, please let me know. I'm here to support your development work."
    elif user_profile['user_type'] == 'business_user':
        return "I'm committed to ensuring your business operations run smoothly. Please don't hesitate to reach out if you need further assistance."
    else:
        return "I hope this helps resolve your issue. If you have any questions or need clarification on any of these steps, I'm here to help."

def create_personalized_fallback(user_profile: Dict, ticket: Dict[str, str]) -> str:
    """Create a personalized fallback response when generation fails."""
    category_specific = {
        'Technical': "technical issue",
        'Billing': "billing inquiry", 
        'Security': "security concern",
        'General': "support request"
    }
    
    issue_type = category_specific.get(ticket.get('category', 'General'), 'inquiry')
    
    if user_profile['urgency'] == 'high':
        return f"I understand your {issue_type} is urgent. Due to a temporary system issue, I'm escalating this directly to our priority support team. You'll receive a detailed response within our expedited timeframe."
    else:
        return f"Thank you for your {issue_type}. While I'm experiencing a temporary processing issue, I want to ensure you receive the best possible assistance. I'm connecting you with a specialist who can provide comprehensive support for your specific situation."

def create_intelligent_error_response(ticket: Dict[str, str], error_details: str) -> str:
    """Create an intelligent error response that doesn't reveal technical details."""
    logger.error(f"Response generation error: {error_details}")
    
    return f"""I apologize for the technical difficulty in processing your request about "{ticket['subject']}". 

To ensure you receive the best possible assistance, I'm immediately escalating your inquiry to our specialist team. They have access to additional resources and can provide comprehensive support for your specific situation.

You can expect a detailed response within our standard timeframe. Thank you for your patience, and we appreciate the opportunity to resolve this for you."""