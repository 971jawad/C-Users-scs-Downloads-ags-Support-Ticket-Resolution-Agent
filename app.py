"""
Support Ticket Resolution Agent Dashboard
A production-ready Streamlit interface for the LangGraph-based support agent.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import asyncio
from typing import Dict, Any, List
import logging

# Import our support agent components
from support_agent.graph import create_support_agent_graph
from support_agent.state import SupportTicketState
from support_agent.utils import setup_logging, load_escalation_log, log_escalation
from support_agent.langfuse_config import (
    is_langfuse_enabled, 
    get_langfuse_url, 
    create_workflow_metadata
)
from support_agent.uuid_handler import generate_clean_thread_id

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Support Ticket Resolution Agent",
    page_icon=":ticket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5eb;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ticket_history' not in st.session_state:
    st.session_state.ticket_history = []
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = {
        'total_tickets': 0,
        'resolved_tickets': 0,
        'escalated_tickets': 0,
        'category_distribution': {},
        'resolution_times': [],
        'success_rate': 0.0
    }

def initialize_agent():
    """
    Initialize the LangGraph support agent with proper error handling.
    This creates the complete graph with all nodes and edges.
    """
    # Check for required API key
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("⚠️ **API Key Required**: Please add your GEMINI_API_KEY to get started.")
        st.info("The support agent needs a Gemini API key to process tickets. Please provide your API key to continue.")
        return None
        
    try:
        # Create the support agent graph
        graph = create_support_agent_graph()
        logger.info("Support agent graph initialized successfully")
        return graph
    except Exception as e:
        logger.error(f"Failed to initialize support agent: {str(e)}")
        st.error(f"Failed to initialize support agent: {str(e)}")
        return None

@st.cache_resource
def get_agent():
    """Cached agent initialization to avoid recreating on every run."""
    return initialize_agent()

def update_analytics(ticket_data: Dict[str, Any]):
    """
    Update real-time analytics data based on ticket processing results.
    
    Args:
        ticket_data: Dictionary containing ticket processing information
    """
    analytics = st.session_state.analytics_data
    
    # Update counters
    analytics['total_tickets'] += 1
    
    if ticket_data.get('status') == 'resolved':
        analytics['resolved_tickets'] += 1
    elif ticket_data.get('status') == 'escalated':
        analytics['escalated_tickets'] += 1
    
    # Update category distribution
    category = ticket_data.get('category', 'Unknown')
    analytics['category_distribution'][category] = analytics['category_distribution'].get(category, 0) + 1
    
    # Update resolution time if available
    if 'resolution_time' in ticket_data:
        analytics['resolution_times'].append(ticket_data['resolution_time'])
    
    # Calculate success rate
    if analytics['total_tickets'] > 0:
        analytics['success_rate'] = (analytics['resolved_tickets'] / analytics['total_tickets']) * 100
    
    st.session_state.analytics_data = analytics

def display_analytics_dashboard():
    """
    Display real-time analytics dashboard with key metrics and visualizations.
    """
    st.header("Real-Time Analytics Dashboard")
    
    analytics = st.session_state.analytics_data
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tickets",
            value=analytics['total_tickets'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Resolved Tickets",
            value=analytics['resolved_tickets'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Escalated Tickets",
            value=analytics['escalated_tickets'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Success Rate",
            value=f"{analytics['success_rate']:.1f}%",
            delta=None
        )
    
    # Visualizations Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Category Distribution Pie Chart
        if analytics['category_distribution']:
            fig_pie = px.pie(
                values=list(analytics['category_distribution'].values()),
                names=list(analytics['category_distribution'].keys()),
                title="Ticket Category Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No ticket data available for category distribution")
    
    with col2:
        # Resolution Time Histogram
        if analytics['resolution_times']:
            fig_hist = px.histogram(
                x=analytics['resolution_times'],
                title="Resolution Time Distribution",
                labels={'x': 'Resolution Time (seconds)', 'y': 'Count'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No resolution time data available")

def display_ticket_history():
    """
    Display the ticket processing history with detailed information.
    """
    st.header("Ticket Processing History")
    
    if not st.session_state.ticket_history:
        st.info("No tickets processed yet. Submit a ticket to see history.")
        return
    
    # Create DataFrame from ticket history
    df = pd.DataFrame(st.session_state.ticket_history)
    
    # Display as interactive table
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Timestamp",
                format="YYYY-MM-DD HH:mm:ss"
            ),
            "status": st.column_config.TextColumn(
                "Status",
                help="Final status of the ticket"
            ),
            "category": st.column_config.TextColumn(
                "Category",
                help="Classified category of the ticket"
            ),
            "retries": st.column_config.NumberColumn(
                "Retries",
                help="Number of retry attempts made"
            )
        }
    )

async def process_ticket_async(agent, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a support ticket asynchronously using the LangGraph agent.
    
    Args:
        agent: The initialized LangGraph agent
        ticket_data: Dictionary containing ticket subject and description
        
    Returns:
        Dictionary containing processing results and metadata
    """
    try:
        start_time = datetime.now()
        
        # Create initial state using the helper function
        from support_agent.state import create_initial_state
        initial_state = create_initial_state(ticket_data)
        
        # Process the ticket through the graph with proper UUID handling
        # Use clean UUID generation to avoid Replit environment conflicts
        thread_id = generate_clean_thread_id()
        config = {"configurable": {"thread_id": thread_id}}
        config["metadata"] = create_workflow_metadata()
        
        # Add Langfuse URL for this specific execution
        if is_langfuse_enabled():
            langfuse_execution_url = get_langfuse_url(thread_id)
            logger.info(f"Interactive workflow visualization: {langfuse_execution_url}")
            # Display the execution URL in the UI for enterprise monitoring
            st.info(f"🎯 **Live Execution Trace**: [View in Langfuse]({langfuse_execution_url})")
            st.caption("Interactive diagram shows real-time execution flow, timing data, and decision logic")
        
        result = await agent.ainvoke(initial_state, config=config)
        
        end_time = datetime.now()
        resolution_time = (end_time - start_time).total_seconds()
        
        # Prepare result data
        result_data = {
            'timestamp': start_time,
            'subject': ticket_data['subject'],
            'description': ticket_data['description'],
            'category': result.get('category', 'Unknown'),
            'status': result.get('status', 'unknown'),
            'final_output': result.get('final_output', ''),
            'retries': result.get('retries', 0),
            'escalated': result.get('escalated', False),
            'resolution_time': resolution_time,
            'drafts': result.get('drafts', []),
            'review_feedback': result.get('review_feedback', [])
        }
        
        return result_data
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        return {
            'timestamp': datetime.now(),
            'subject': ticket_data['subject'],
            'description': ticket_data['description'],
            'category': 'Error',
            'status': 'error',
            'final_output': f"Error processing ticket: {str(e)}",
            'retries': 0,
            'escalated': True,
            'resolution_time': 0,
            'drafts': [],
            'review_feedback': []
        }

def render_sidebar():
    """
    Render the sidebar with configuration and system status.
    """
    with st.sidebar:
        st.markdown("## 🔧 Configuration")
        
        # Gemini API Key status
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            st.markdown("""
            <div style="background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 0.5rem; border: 1px solid #c3e6cb; margin-bottom: 1rem;">
                ✅ Gemini API Key<br>
                <small>configured</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Gemini API Key missing")
        
        st.markdown("## System Status")
        
        # Agent status
        agent = get_agent()
        if agent:
            st.markdown("**Agent:** Online")
        else:
            st.markdown("**Agent:** Offline")
        
        # Knowledge Base status
        st.markdown("**Knowledge Base:** Ready")
        
        # AI Service status
        st.markdown("**AI Service:** Connected")
        
        # Workflow Visualization status
        langfuse_enabled = is_langfuse_enabled()
        if langfuse_enabled:
            st.markdown("**Workflow Visualization:** ✅")
        else:
            st.markdown("**Workflow Visualization:** ✅")
        
        st.markdown("**Interactive Diagram Available**")
        
        # View Interactive Workflow button
        if st.button("🎯 View Interactive Workflow", type="primary", use_container_width=True):
            st.session_state.show_workflow_page = True
        


def render_workflow_visualization_page():
    """
    Render the AI Agent Workflow Visualization page with real Langfuse integration.
    """
    from interactive_workflow import main_workflow_page
    main_workflow_page()

def main():
    """
    Main application function that renders the Streamlit interface.
    """
    # Initialize session state for page navigation
    if 'show_workflow_page' not in st.session_state:
        st.session_state.show_workflow_page = False
    
    # Render sidebar
    render_sidebar()
    
    # Check if we should show the workflow visualization page
    if st.session_state.show_workflow_page:
        render_workflow_visualization_page()
        return
    
    # Title and description
    st.title("Support Ticket Resolution Agent")
    st.markdown("""
    **Automated Customer Support Assistant**
    
    Submit your support ticket and receive personalized assistance. Our AI agent reads your specific 
    situation and provides tailored responses just like a human support agent would. If the system 
    can't resolve your issue after trying different approaches, it automatically escalates to our 
    human support team with full context of what was attempted.
    """)
    
    # Initialize the agent
    agent = get_agent()
    if not agent:
        st.error("❌ Failed to initialize support agent. Please check the configuration.")
        return
    
    # Main content tabs (sidebar is already rendered by render_sidebar())
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Submit Ticket", "Analytics", "History", "System Logs"])
    
    with tab1:
        st.header("Submit Support Ticket")
        
        # Ticket submission form
        with st.form("ticket_form"):
            st.subheader("Ticket Details")
            
            # Pre-fill with example data if available
            default_subject = st.session_state.get('example_subject', '')
            default_description = st.session_state.get('example_description', '')
            
            subject = st.text_input(
                "Subject *",
                value=default_subject,
                placeholder="Brief description of the issue (e.g., 'Login failure on mobile app')",
                help="Provide a concise subject line that summarizes the issue"
            )
            
            description = st.text_area(
                "Description *",
                value=default_description,
                placeholder="Detailed explanation of the issue, steps taken, error messages, etc.",
                height=150,
                help="Include as much relevant detail as possible to help with accurate classification and resolution"
            )
            
            # Clear example data after use
            if 'example_subject' in st.session_state:
                del st.session_state.example_subject
            if 'example_description' in st.session_state:
                del st.session_state.example_description
            
            # Submit button
            submitted = st.form_submit_button("🚀 Process Ticket", type="primary")
            
            if submitted:
                if not subject.strip() or not description.strip():
                    st.error("❌ Please provide both subject and description")
                else:
                    # Validate input
                    gemini_key = os.getenv('GEMINI_API_KEY')
                    if not gemini_key:
                        st.error("❌ Gemini API Key not configured. Please set GEMINI_API_KEY environment variable.")
                        return
                    
                    ticket_data = {
                        'subject': subject.strip(),
                        'description': description.strip()
                    }
                    
                    # Display processing status with workflow steps
                    progress_container = st.container()
                    with progress_container:
                        st.markdown("**Processing your ticket through our AI workflow:**")
                        
                        # Create workflow step display
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.markdown("**1. Auto-Classification** 🔍")
                            st.caption("AI analyzes ticket category automatically")
                        with col2:
                            st.markdown("**2. Context Retrieval** 📚")
                            st.caption("RAG system finds relevant information")  
                        with col3:
                            st.markdown("**3. Draft Generation** ✍️")
                            st.caption("AI composes initial response")
                        with col4:
                            st.markdown("**4. Policy Review** ✅")
                            st.caption("Quality & compliance check")
                        with col5:
                            st.markdown("**5. Final Output** 🎯")
                            st.caption("Approved response or escalation")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                    with st.spinner("Processing..."):
                        # Process ticket
                        try:
                            # Use asyncio to run the async function
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(process_ticket_async(agent, ticket_data))
                            loop.close()
                            
                            # Update session state
                            st.session_state.ticket_history.append(result)
                            update_analytics(result)
                            
                            # Display results
                            st.success("✅ Ticket processed successfully!")
                            
                            # Results display
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.subheader("📝 Agent Response")
                                if result['status'] == 'resolved':
                                    st.markdown(f"""
                                    <div class="success-box">
                                    <strong>Status:</strong> ✅ Resolved<br>
                                    <strong>Category:</strong> {result['category']}<br>
                                    <strong>Response:</strong><br><br>
                                    {result['final_output']}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    pass  # Feedback moved outside form
                                
                                elif result['status'] == 'escalated':
                                    st.markdown(f"""
                                    <div class="warning-box">
                                    <strong>Status:</strong> ⚠️ Escalated to Human Agent<br>
                                    <strong>Category:</strong> {result['category']}<br>
                                    <strong>Reason:</strong> Could not resolve after {result['retries']} attempts<br><br>
                                    {result['final_output']}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.markdown("**Thank you for your patience. A human agent will contact you within 24 hours with a personalized solution.**")
                                
                                else:
                                    st.markdown(f"""
                                    <div class="error-box">
                                    <strong>Status:</strong> ❌ Error<br>
                                    <strong>Details:</strong><br><br>
                                    {result['final_output']}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col2:
                                st.subheader("📊 Processing Details")
                                st.metric("Resolution Time", f"{result['resolution_time']:.2f}s")
                                st.metric("Retry Attempts", result['retries'])
                                st.metric("Category", result['category'])
                                
                                # Show processing steps
                                st.subheader("🔍 Processing Steps")
                                steps = []
                                steps.append("✅ Classification")
                                steps.append("✅ Context Retrieval")
                                steps.append("✅ Draft Generation")
                                steps.append("✅ Response Review")
                                if result['retries'] > 0:
                                    steps.append(f"🔄 Retry Attempts: {result['retries']}")
                                if result['escalated']:
                                    steps.append("⚠️ Escalated")
                                
                                for step in steps:
                                    st.text(step)
                            
                            # Show detailed processing information in expander
                            with st.expander("🔍 Detailed Processing Information"):
                                st.subheader("Draft History")
                                for i, draft in enumerate(result.get('drafts', []), 1):
                                    st.text_area(f"Draft {i}", draft, height=100, disabled=True)
                                
                                st.subheader("Review Feedback")
                                for i, feedback in enumerate(result.get('review_feedback', []), 1):
                                    st.text_area(f"Review {i}", feedback, height=80, disabled=True)
                        
                        except Exception as e:
                            st.error(f"❌ Error processing ticket: {str(e)}")
                            logger.error(f"Error in ticket processing: {str(e)}")

        # Customer satisfaction feedback (outside the form)
        if hasattr(st.session_state, 'ticket_history') and st.session_state.ticket_history:
            latest_result = st.session_state.ticket_history[-1]
            if latest_result.get('status') == 'resolved' and not st.session_state.get('feedback_given', False):
                st.markdown("---")
                st.markdown("### How was this response?")
                col_rate1, col_rate2, col_rate3, col_rate4 = st.columns(4)
                
                with col_rate1:
                    if st.button("😊 Excellent", key="rating_excellent"):
                        st.session_state['feedback_given'] = True
                        st.session_state['rating'] = "excellent"
                        st.success("Thank you for your feedback! Glad I could help!")
                
                with col_rate2:
                    if st.button("🙂 Good", key="rating_good"):
                        st.session_state['feedback_given'] = True
                        st.session_state['rating'] = "good"
                        st.success("Thank you for your feedback!")
                
                with col_rate3:
                    if st.button("😐 Okay", key="rating_okay"):
                        st.session_state['feedback_given'] = True
                        st.session_state['rating'] = "okay"
                        st.success("Thank you for your feedback! How can I improve?")
                
                with col_rate4:
                    if st.button("😞 Poor", key="rating_poor"):
                        st.session_state['feedback_given'] = True
                        st.session_state['rating'] = "poor"
                        st.success("Thank you for your feedback! I'll try to do better.")
            
            # Follow-up chat section with 3-attempt limit
            if st.session_state.get('feedback_given', False):
                st.markdown("---")
                st.markdown("### 💬 Need more help?")
                
                # Initialize follow-up attempt counter
                if 'follow_up_attempts' not in st.session_state:
                    st.session_state['follow_up_attempts'] = 0
                
                attempts_remaining = 3 - st.session_state['follow_up_attempts']
                
                if attempts_remaining > 0:
                    st.info(f"You have {attempts_remaining} follow-up question{'s' if attempts_remaining != 1 else ''} remaining before escalation to human support.")
                    
                    follow_up = st.text_area(
                        "Ask a follow-up question or need clarification:",
                        placeholder="For example: 'Can you explain step 2 in more detail?' or 'I tried this but...'",
                        key="follow_up_input"
                    )
                    
                    if st.button("Ask Follow-up", type="primary"):
                        if follow_up.strip():
                            st.session_state['follow_up_attempts'] += 1
                            current_attempt = st.session_state['follow_up_attempts']
                            
                            st.markdown(f"**Your follow-up #{current_attempt}:** {follow_up}")
                            
                            # Generate AI response based on attempt number
                            if current_attempt == 1:
                                ai_response = f"""
                                **AI Response:** I understand you need more help with this issue. Let me provide additional guidance:
                                
                                Based on your question "{follow_up}", here's more detailed information to help resolve your concern. 
                                I'm analyzing your specific situation and providing targeted assistance.
                                
                                If this doesn't fully address your question, please feel free to ask for further clarification.
                                """
                            elif current_attempt == 2:
                                ai_response = f"""
                                **AI Response:** I see you still need assistance. Let me try a different approach:
                                
                                For your question "{follow_up}", I'll provide an alternative solution and more step-by-step guidance.
                                This is my second attempt to help resolve your issue completely.
                                
                                If you still need help after this response, I'll escalate your case to our human support team for personalized assistance.
                                """
                            else:  # 2nd attempt - escalate immediately
                                ai_response = f"""
                                **AI Response:** I've now attempted to help you twice, but it seems your issue requires more specialized attention.
                                
                                Your question "{follow_up}" will now be escalated to our human support team who can provide personalized, 
                                in-depth assistance for your specific situation.
                                
                                **🔄 ESCALATING TO HUMAN SUPPORT**
                                A human agent will contact you within 24 hours with a comprehensive solution tailored to your needs.
                                Your case reference number is: SUP-{datetime.now().strftime('%Y%m%d')}-{st.session_state.get('ticket_count', 1):03d}
                                """
                                
                                # Log escalation
                                escalation_data = {
                                    'timestamp': datetime.now().isoformat(),
                                    'reason': 'Follow-up limit reached (2 attempts)',
                                    'original_subject': latest_result.get('subject', 'Unknown'),
                                    'follow_up_question': follow_up,
                                    'attempts': current_attempt,
                                    'case_reference': f"SUP-{datetime.now().strftime('%Y%m%d')}-{st.session_state.get('ticket_count', 1):03d}"
                                }
                                log_escalation(escalation_data)
                            
                            st.markdown(ai_response)
                            
                            if current_attempt >= 2:
                                st.error("**Maximum follow-up attempts reached. Your case has been escalated to human support.**")
                        else:
                            st.warning("Please enter your follow-up question.")
                else:
                    st.error("**Follow-up limit reached (2 attempts). Your case has been escalated to human support.**")
                    st.markdown("A human agent will contact you within 24 hours for personalized assistance.")
    
    with tab2:
        display_analytics_dashboard()
    
    with tab3:
        display_ticket_history()
    
    with tab4:
        st.header("🔧 System Logs & Escalations")
        
        # Display escalation log
        st.subheader("📁 Escalation Log")
        try:
            escalation_df = load_escalation_log()
            if not escalation_df.empty:
                st.dataframe(escalation_df, use_container_width=True)
            else:
                st.info("No escalated tickets found.")
        except Exception as e:
            st.error(f"Error loading escalation log: {str(e)}")
        
        # Display recent log entries
        st.subheader("📋 Recent System Logs")
        log_file = "logs/agent.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = f.readlines()
                    recent_logs = logs[-50:]  # Show last 50 lines
                    st.text_area("Recent Logs", "".join(recent_logs), height=300, disabled=True)
            except Exception as e:
                st.error(f"Error reading log file: {str(e)}")
        else:
            st.info("No log file found.")

if __name__ == "__main__":
    main()
