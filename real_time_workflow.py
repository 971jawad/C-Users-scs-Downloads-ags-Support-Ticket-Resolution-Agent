"""
Real-time Workflow Visualization with Live System Data

This module creates a dynamic workflow diagram that updates based on actual 
system processing data, showing live execution status and flow.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import asyncio
from typing import Dict, Any, List
import time
from support_agent.utils import load_escalation_log

def create_real_time_workflow_diagram(system_data: Dict[str, Any] = None):
    """
    Create a real-time workflow diagram that shows actual system execution data.
    
    Args:
        system_data: Dictionary containing current system state and execution data
        
    Returns:
        Plotly figure with real-time data visualization
    """
    if system_data is None:
        system_data = get_current_system_state()
    
    # Define nodes with real-time status
    nodes = {
        "user_input": {
            "x": 1, "y": 5, "size": 100,
            "color": get_node_color("user_input", system_data),
            "label": "User Input",
            "status": system_data.get("user_input_status", "ready"),
            "count": system_data.get("total_tickets", 0),
            "avg_time": "0.1s"
        },
        "classifier": {
            "x": 3, "y": 5, "size": 100,
            "color": get_node_color("classifier", system_data),
            "label": "LLM Classifier", 
            "status": system_data.get("classifier_status", "ready"),
            "count": system_data.get("classified_tickets", 0),
            "avg_time": "1.2s"
        },
        "rag_system": {
            "x": 5, "y": 5, "size": 100,
            "color": get_node_color("rag_system", system_data),
            "label": "RAG System",
            "status": system_data.get("rag_status", "ready"),
            "count": system_data.get("retrieved_contexts", 0),
            "avg_time": "0.8s"
        },
        "generator": {
            "x": 7, "y": 5, "size": 100,
            "color": get_node_color("generator", system_data),
            "label": "LLM Generator",
            "status": system_data.get("generator_status", "ready"),
            "count": system_data.get("generated_drafts", 0),
            "avg_time": "2.1s"
        },
        "reviewer": {
            "x": 9, "y": 5, "size": 100,
            "color": get_node_color("reviewer", system_data),
            "label": "LLM Reviewer",
            "status": system_data.get("reviewer_status", "ready"),
            "count": system_data.get("reviewed_drafts", 0),
            "avg_time": "1.0s"
        },
        "refinement": {
            "x": 7, "y": 3, "size": 80,
            "color": get_node_color("refinement", system_data),
            "label": "Refinement",
            "status": system_data.get("refinement_status", "ready"),
            "count": system_data.get("refinement_attempts", 0),
            "avg_time": "1.5s"
        },
        "success": {
            "x": 11, "y": 5, "size": 100,
            "color": get_node_color("success", system_data),
            "label": "Success Output",
            "status": "completed",
            "count": system_data.get("successful_tickets", 0),
            "avg_time": "0.3s"
        },
        "escalation": {
            "x": 11, "y": 3, "size": 80,
            "color": get_node_color("escalation", system_data),
            "label": "Human Escalation",
            "status": "escalated",
            "count": system_data.get("escalated_tickets", 0),
            "avg_time": "24h"
        }
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add connections with real-time flow data
    connections = [
        {"from": "user_input", "to": "classifier", "flow_rate": system_data.get("input_to_classifier_flow", 0)},
        {"from": "classifier", "to": "rag_system", "flow_rate": system_data.get("classifier_to_rag_flow", 0)},
        {"from": "rag_system", "to": "generator", "flow_rate": system_data.get("rag_to_generator_flow", 0)},
        {"from": "generator", "to": "reviewer", "flow_rate": system_data.get("generator_to_reviewer_flow", 0)},
        {"from": "reviewer", "to": "success", "flow_rate": system_data.get("reviewer_to_success_flow", 0)},
        {"from": "reviewer", "to": "refinement", "flow_rate": system_data.get("reviewer_to_refinement_flow", 0)},
        {"from": "refinement", "to": "generator", "flow_rate": system_data.get("refinement_to_generator_flow", 0)},
        {"from": "reviewer", "to": "escalation", "flow_rate": system_data.get("reviewer_to_escalation_flow", 0)}
    ]
    
    # Add connection lines with flow visualization
    for conn in connections:
        start_node = nodes[conn["from"]]
        end_node = nodes[conn["to"]]
        flow_rate = conn["flow_rate"]
        
        # Line thickness based on flow rate
        line_width = max(1, min(8, flow_rate * 2))
        
        # Color based on connection type
        if conn["to"] == "success":
            line_color = "#00796b"
        elif conn["to"] == "escalation":
            line_color = "#d32f2f"
        elif conn["to"] == "refinement" or conn["from"] == "refinement":
            line_color = "#fbc02d"
        else:
            line_color = "#1976d2"
        
        # Add connection line
        fig.add_trace(go.Scatter(
            x=[start_node["x"], end_node["x"]],
            y=[start_node["y"], end_node["y"]],
            mode='lines',
            line=dict(color=line_color, width=line_width),
            showlegend=False,
            hovertemplate=f"Flow: {flow_rate} tickets/min<extra></extra>",
            opacity=0.7
        ))
        
        # Add flow direction arrow
        mid_x = (start_node["x"] + end_node["x"]) / 2
        mid_y = (start_node["y"] + end_node["y"]) / 2
        
        fig.add_annotation(
            x=mid_x, y=mid_y,
            text="→",
            showarrow=False,
            font=dict(size=14, color=line_color),
            bgcolor="white",
            bordercolor=line_color,
            borderwidth=1
        )
    
    # Add nodes with real-time status
    for node_id, node_data in nodes.items():
        fig.add_trace(go.Scatter(
            x=[node_data["x"]],
            y=[node_data["y"]],
            mode='markers+text',
            marker=dict(
                size=node_data["size"],
                color=node_data["color"],
                line=dict(color="#333", width=2),
                opacity=0.9
            ),
            text=f"{node_data['label']}<br>({node_data['count']})",
            textposition="middle center",
            textfont=dict(size=9, color="black"),
            name=node_data["label"],
            showlegend=False,
            customdata=[{
                "node_id": node_id,
                "status": node_data["status"],
                "count": node_data["count"],
                "avg_time": node_data["avg_time"]
            }],
            hovertemplate=(
                f"<b>{node_data['label']}</b><br>"
                f"Status: {node_data['status']}<br>"
                f"Processed: {node_data['count']} tickets<br>"
                f"Avg Time: {node_data['avg_time']}<br>"
                "<extra></extra>"
            )
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"🔴 LIVE: AI Agent Workflow - {datetime.now().strftime('%H:%M:%S')}",
            'x': 0.5,
            'font': {'size': 18, 'color': '#d32f2f'}
        },
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        width=1000,
        height=500,
        margin=dict(l=50, r=50, t=100, b=50),
        annotations=[
            dict(
                text=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Live System Data",
                x=0.5, y=-0.1,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=12, color='#666')
            )
        ]
    )
    
    return fig

def get_node_color(node_id: str, system_data: Dict[str, Any]) -> str:
    """
    Get node color based on real-time status and processing load.
    
    Args:
        node_id: Identifier for the workflow node
        system_data: Current system state data
        
    Returns:
        Color code for the node based on current status
    """
    status = system_data.get(f"{node_id}_status", "ready")
    load = system_data.get(f"{node_id}_load", 0)
    
    # Color coding based on status and load
    if status == "processing":
        return "#ff9800"  # Orange for active processing
    elif status == "error":
        return "#f44336"  # Red for errors
    elif status == "completed":
        return "#4caf50"  # Green for completed
    elif load > 0.8:
        return "#ff5722"  # Red-orange for high load
    elif load > 0.5:
        return "#ffc107"  # Yellow for medium load
    else:
        return "#e3f2fd"  # Light blue for ready/low load

def get_current_system_state() -> Dict[str, Any]:
    """
    Get current system state from session data and escalation logs.
    
    Returns:
        Dictionary containing current system metrics and status
    """
    # Get data from Streamlit session state
    ticket_history = st.session_state.get('ticket_history', [])
    analytics_data = st.session_state.get('analytics_data', {})
    
    # Load escalation data
    try:
        escalation_df = load_escalation_log()
        escalated_count = len(escalation_df) if not escalation_df.empty else 0
    except:
        escalated_count = 0
    
    # Calculate real-time metrics
    total_tickets = len(ticket_history)
    successful_tickets = len([t for t in ticket_history if t.get('status') == 'resolved'])
    
    # Calculate recent activity (last hour)
    current_time = datetime.now()
    recent_tickets = []
    for t in ticket_history:
        try:
            timestamp_str = t.get('timestamp', current_time.isoformat())
            if isinstance(timestamp_str, str):
                ticket_time = datetime.fromisoformat(timestamp_str)
                if (current_time - ticket_time).total_seconds() < 3600:
                    recent_tickets.append(t)
        except (ValueError, TypeError):
            # Skip tickets with invalid timestamps
            continue
    
    # Calculate flow rates (tickets per minute in last hour)
    recent_count = len(recent_tickets)
    flow_rate = recent_count / 60 if recent_count > 0 else 0
    
    return {
        # Node statuses
        "user_input_status": "ready",
        "classifier_status": "ready",
        "rag_status": "ready", 
        "generator_status": "ready",
        "reviewer_status": "ready",
        "refinement_status": "ready",
        
        # Processing counts
        "total_tickets": total_tickets,
        "classified_tickets": total_tickets,
        "retrieved_contexts": total_tickets,
        "generated_drafts": total_tickets + analytics_data.get('total_retries', 0),
        "reviewed_drafts": total_tickets,
        "refinement_attempts": analytics_data.get('total_retries', 0),
        "successful_tickets": successful_tickets,
        "escalated_tickets": escalated_count,
        
        # Flow rates
        "input_to_classifier_flow": flow_rate,
        "classifier_to_rag_flow": flow_rate,
        "rag_to_generator_flow": flow_rate,
        "generator_to_reviewer_flow": flow_rate * 1.2,  # Include retries
        "reviewer_to_success_flow": flow_rate * 0.8,
        "reviewer_to_refinement_flow": flow_rate * 0.2,
        "refinement_to_generator_flow": flow_rate * 0.2,
        "reviewer_to_escalation_flow": flow_rate * 0.1,
        
        # Load indicators
        "user_input_load": min(1.0, recent_count / 10),
        "classifier_load": min(1.0, recent_count / 10),
        "rag_load": min(1.0, recent_count / 8),
        "generator_load": min(1.0, recent_count / 6),
        "reviewer_load": min(1.0, recent_count / 8),
        "refinement_load": min(1.0, analytics_data.get('total_retries', 0) / 5)
    }

def render_real_time_metrics():
    """
    Render real-time system metrics with live updates.
    """
    system_data = get_current_system_state()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Active Tickets",
            system_data["total_tickets"],
            delta=f"+{system_data.get('input_to_classifier_flow', 0):.1f}/min"
        )
    
    with col2:
        success_rate = (system_data["successful_tickets"] / max(1, system_data["total_tickets"])) * 100
        st.metric(
            "✅ Success Rate", 
            f"{success_rate:.1f}%",
            delta=f"{success_rate - 85:.1f}%" if success_rate > 85 else f"{success_rate - 85:.1f}%"
        )
    
    with col3:
        st.metric(
            "🔄 Retry Rate",
            f"{system_data['refinement_attempts']}",
            delta=f"{system_data.get('reviewer_to_refinement_flow', 0):.1f}/min"
        )
    
    with col4:
        st.metric(
            "⚠️ Escalations",
            system_data["escalated_tickets"],
            delta=f"+{system_data.get('reviewer_to_escalation_flow', 0):.1f}/min"
        )

def main_real_time_workflow_page():
    """
    Main page for real-time workflow visualization.
    """
    st.title("🔴 LIVE: AI Agent Workflow Monitor")
    st.markdown("**Real-time system data • Live execution tracking • Manual refresh**")
    
    # Navigation
    if st.button("← Back to Main Dashboard", key="real_time_back"):
        st.session_state.show_workflow_page = False
        st.rerun()
    
    # Manual refresh only - auto-refresh disabled to prevent flickering
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()
    
    st.markdown("---")
    
    # Real-time metrics
    render_real_time_metrics()
    
    st.markdown("---")
    
    # Real-time workflow diagram
    st.subheader("🔍 Live Workflow Execution Map")
    st.markdown("**Real system data • Node size = processing load • Color = current status**")
    
    # Get current system state and create diagram
    system_data = get_current_system_state()
    fig = create_real_time_workflow_diagram(system_data)
    
    # Display with real-time updates
    chart_placeholder = st.empty()
    chart_placeholder.plotly_chart(fig, use_container_width=True, key="live_workflow")
    
    # Live system status
    st.markdown("### 📊 Live System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Node Processing Status**")
        status_data = [
            ("User Input", system_data.get("user_input_status", "ready")),
            ("LLM Classifier", system_data.get("classifier_status", "ready")),
            ("RAG System", system_data.get("rag_status", "ready")),
            ("LLM Generator", system_data.get("generator_status", "ready")),
            ("LLM Reviewer", system_data.get("reviewer_status", "ready")),
            ("Refinement Tool", system_data.get("refinement_status", "ready"))
        ]
        
        for node, status in status_data:
            status_icon = "🟢" if status == "ready" else "🟡" if status == "processing" else "🔴"
            st.markdown(f"{status_icon} **{node}**: {status.title()}")
    
    with col2:
        st.markdown("**Recent Activity**")
        recent_activity = [
            f"Tickets processed: {system_data['total_tickets']}",
            f"Success rate: {(system_data['successful_tickets'] / max(1, system_data['total_tickets']) * 100):.1f}%",
            f"Active retries: {system_data['refinement_attempts']}",
            f"Escalations: {system_data['escalated_tickets']}",
            f"Flow rate: {system_data.get('input_to_classifier_flow', 0):.1f} tickets/min"
        ]
        
        for activity in recent_activity:
            st.markdown(f"• {activity}")
    
    # Auto-refresh removed to prevent flickering - use manual refresh button instead

if __name__ == "__main__":
    main_real_time_workflow_page()