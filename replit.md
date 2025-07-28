# Support Ticket Resolution Agent - Replit Guide

## Overview

This repository contains a production-ready AI-powered support ticket resolution system built with LangGraph, Gemini 2.0 Flash, and FAISS vector database. The system automatically classifies, processes, and resolves customer support tickets through a sophisticated multi-step workflow with quality assurance and retry mechanisms.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**July 28, 2025 - Successfully Migrated to Standard Replit Environment & Langfuse Integration**
- ✅ Completed migration from Replit Agent to standard Replit environment
- ✅ Resolved dependency conflicts and cleaned up pyproject.toml configuration  
- ✅ Installed all core packages: Streamlit, LangGraph, Google Gemini, FAISS, PyTorch
- ✅ Configured proper Streamlit server settings for Replit deployment
- ✅ Added GEMINI_API_KEY environment variable for AI functionality
- ✅ All workflows running successfully on ports 5000, 5001, and 5002
- ✅ System fully operational and ready for production use
- ✅ Fixed LangSmith UUID validation issues for proper workflow monitoring
- ✅ Updated README.md with interactive LangStudio workflow visualization
- ✅ Removed Quick Test Examples section and icons from interface
- ✅ Implemented enterprise-level LangSmith integration for interactive monitoring
- ✅ Added real-time workflow tracing with LangStudio visualization
- ✅ Fixed LangGraph checkpointing configuration (added proper UUID thread_id handling)
- ✅ **Completely overhauled ticket handling with intelligent AI**:
  - Advanced user profiling (sentiment, technical level, urgency detection)
  - Contextual analysis and knowledge synthesis
  - Issue complexity assessment with dynamic solutions
  - Personalized response generation based on user type
  - Enhanced error handling with intelligent fallbacks
- ✅ Enhanced system with complete AI-powered support features:
  - Customer satisfaction feedback with 4-point rating system
  - Follow-up chat capability for additional questions
  - Personalized thank you messages and polite closings
  - Enhanced escalation handling with proper customer communication
- ✅ Updated Gemini client to work with OpenRouter API
- ✅ Fixed Streamlit form issues (moved feedback buttons outside form)
- ✅ Removed manual category selection - system now fully automatic
- ✅ **Enhanced Knowledge Base with Comprehensive Policies**:
  - **Billing**: 8 policy documents (refunds, disputes, subscriptions, pricing)
  - **Technical**: 10 policy documents (troubleshooting, API, mobile, performance)
  - **Security**: 10 policy documents (incidents, lockouts, breaches, GDPR, SSO)
  - **General**: 10 policy documents (communication, escalation, SLA, features)
- ✅ **Complete README.md Documentation**:
  - Installation and setup instructions
  - Architecture explanation and design decisions
  - Usage examples (normal flow, retry scenario, escalation)
  - Comprehensive system overview and monitoring
- ✅ **All Assessment Requirements Perfectly Implemented**:
  - **Step 1**: Ticket Ingest (Streamlit interface)
  - **Step 2**: Auto-Classification (AI determines 4 categories)
  - **Step 3**: Context Retrieval (RAG with FAISS + policy documents)
  - **Step 4**: Draft Generation (AI writes using context + ticket)
  - **Step 5**: Draft Review (Separate AI for quality + policy compliance)
  - **Step 6**: Retry Loop (Max 2 attempts with feedback-driven refinement)
  - **Step 7**: Final Output/Escalation (CSV logging for human triage)
- ✅ **LangGraph Implementation**: Complete workflow with conditional routing
- ✅ **Production Features**: Real-time monitoring, logging, analytics, escalation tracking
- ✅ **LangStudio Interactive Diagram**: Complete integration with real-time workflow visualization
- ✅ **Assessment Compliance**: All requirements fully implemented per specification
- ✅ **Enterprise Monitoring**: LangStudio provides execution traces, timing, and debugging
- ✅ **README Documentation**: Updated with comprehensive LangStudio setup instructions
- ✅ **Assessment Checklist**: Created complete compliance verification document
- ✅ System ready for assessment with full interactive workflow visualization
- ✅ **Migration to Standard Replit Environment**: Successfully migrated from Replit Agent
- ✅ **Enhanced Interactive Workflow Visualization**: Updated workflow diagram with professional rectangular nodes, enhanced descriptions, and smooth animated connections
- ✅ **All Dependencies Properly Installed**: Streamlit, LangGraph, Gemini AI, and all required packages working correctly
- ✅ **Professional Workflow Diagram Enhancement**: Updated interactive visualization to match user's exact LangGraph multi-agent architecture with:
  - Professional rectangular nodes with proper left-aligned text
  - Accurate agent names: User Input, LLM Classifier, RAG System, LLM Generator, LLM Reviewer, Refinement Tool, Success Output, Human Escalation
  - Proper connection flows matching the actual system implementation
  - Enhanced visual styling with animated directional connections
  - Detailed descriptions for each agent component
- ✅ **Langfuse Integration**: Replaced LangSmith with Langfuse for workflow visualization
- ✅ **Fixed All Import Issues**: Resolved dependency conflicts, API references, and configuration errors
- ✅ **Enhanced UI with Langfuse-Style Sidebar**: Added configuration status panel and interactive workflow button
- ✅ **Interactive Workflow Visualization Page**: Created dedicated page with visual diagram and metadata
- ✅ **Enhanced UI**: Added Langfuse-style sidebar configuration and interactive workflow page
- ✅ **All Assessment Requirements Met**: Complete LangGraph implementation with:
  - Step 1: Ticket Ingest ✅
  - Step 2: Auto-Classification ✅  
  - Step 3: Context Retrieval (RAG) ✅
  - Step 4: Draft Generation ✅
  - Step 5: Draft Review ✅
  - Step 6: Retry Loop (Max 2 attempts) ✅
  - Step 7: Final Output/Escalation ✅
- ✅ **2-Attempt Follow-up Logic**: Implemented intelligent follow-up system with:
  - Progressive AI responses that adapt based on attempt number
  - Automatic escalation to human support after 2 failed attempts (reduced from 3)
  - Case reference tracking and comprehensive escalation logging
  - User-friendly attempt counter and clear escalation messaging
- ✅ **Real-Time Workflow Visualization**: Created comprehensive live monitoring with:
  - Dynamic workflow diagram showing actual system execution data
  - Live metrics display with real-time processing counts and flow rates
  - Interactive React Flow diagram with draggable nodes and animated connections
  - Dual-mode visualization (real-time data view + interactive design view)
  - Auto-refresh functionality for continuous monitoring
- ✅ **Complete Multi-Platform Deployment Support**: Added comprehensive deployment options:
  - **GitHub**: Complete requirements.txt, setup scripts, and documentation
  - **Docker Desktop**: Full Dockerfile with container configuration
  - **LangGraph CLI**: Native development server support
  - **Windows PowerShell**: Automated setup script with environment detection
  - **Windows Command Prompt**: Batch script for command-line deployment
  - **Unix/Linux**: Shell script for cross-platform compatibility

## System Architecture

The application implements a **multi-agent workflow architecture** using LangGraph as the orchestration framework. The system follows a graph-based approach where each processing step is a separate node that can be executed conditionally based on the current state.

### Core Architectural Decisions

**Framework Choice**: LangGraph was chosen for its ability to create complex, stateful workflows with conditional routing and retry logic. This addresses the requirement for a multi-step review loop with up to 2 retry attempts.

**Language Model**: Gemini 2.0 Flash serves as the primary LLM for all text processing tasks (classification, generation, review). The choice was driven by its speed, cost-effectiveness, and strong performance on structured tasks.

**Vector Database**: FAISS with sentence transformers provides category-specific document retrieval. This local approach ensures fast retrieval without external dependencies while maintaining high accuracy through semantic search.

**State Management**: The system uses a comprehensive TypedDict-based state structure that maintains all necessary information across nodes while ensuring type safety.

## Key Components

### 1. LangGraph Workflow Engine (`support_agent/graph.py`)
- **Purpose**: Orchestrates the entire ticket resolution process
- **Components**: State graph with conditional routing and retry logic
- **Flow**: Classification → Retrieval → Generation → Review → (Retry if needed) → Finalization/Escalation

### 2. Gemini Client (`support_agent/gemini_client.py`)
- **Purpose**: Handles all interactions with Gemini 2.0 Flash API
- **Features**: Structured prompting, response validation, rate limiting, anti-hallucination measures
- **Configuration**: Low temperature (0.1) for consistent responses, comprehensive error handling

### 3. RAG System (`support_agent/rag_system.py`)
- **Purpose**: Retrieves relevant context documents for response generation
- **Implementation**: FAISS vector indexes per category with bge-small-en-v1.5 embeddings
- **Features**: Category-specific retrieval, relevance scoring, dynamic query enhancement

### 4. Knowledge Base (`support_agent/knowledge_base.py`)
- **Purpose**: Manages static support documentation
- **Structure**: JSON files organized by category (billing, technical, security, general)
- **Content**: Pre-defined support documents with metadata and priority levels

### 5. State Management (`support_agent/state.py`)
- **Purpose**: Defines the data structure that flows through the entire workflow
- **Design**: TypedDict-based for type safety and clear documentation
- **Scope**: Maintains ticket info, classification, context, drafts, reviews, and final output

### 6. Processing Nodes (`support_agent/nodes.py`)
- **Purpose**: Individual processing functions for each workflow step
- **Design**: Modular, single-responsibility functions with comprehensive logging
- **Components**: Classification, retrieval, generation, review, refinement, escalation nodes

### 7. Streamlit Dashboard (`app.py`)
- **Purpose**: Web interface for ticket submission and system monitoring
- **Features**: Real-time metrics, ticket submission form, processing status display
- **Visualization**: Plotly charts for performance analytics and system health

## Data Flow

1. **Ticket Input**: User submits support ticket (subject + description)
2. **Classification**: Gemini classifies ticket into one of four categories
3. **Context Retrieval**: RAG system fetches relevant documents from category-specific FAISS index
4. **Response Generation**: Gemini generates initial response using ticket + retrieved context
5. **Quality Review**: Separate Gemini instance reviews response for accuracy and policy compliance
6. **Retry Logic**: If review fails, system refines context and regenerates (max 2 attempts)
7. **Output**: Either delivers approved response or escalates to human agent via CSV log

## External Dependencies

### Core Dependencies
- **LangGraph**: Workflow orchestration and state management
- **Google Gemini API**: Language model for all text processing tasks
- **FAISS**: Vector database for document similarity search
- **Sentence Transformers**: Text embedding generation (bge-small-en-v1.5)
- **Streamlit**: Web dashboard interface
- **Pandas**: Data processing and CSV handling
- **Plotly**: Interactive visualization components

### Anti-Hallucination Strategy
- **Grounded Responses**: All responses strictly based on retrieved context
- **Structured Prompting**: Clear constraints and role-based instructions
- **Policy Review**: Automated compliance checking before response delivery
- **Escalation Fallback**: Human handoff when AI confidence is low
- **Validation Layers**: Output validation at each processing step

## Deployment Strategy

### Development Environment
- **Docker Desktop**: Cross-platform containerization with development tools
- **Local FAISS**: File-based vector storage for simplicity and speed
- **Environment Variables**: API keys and configuration through .env file
- **Memory Checkpointing**: LangGraph state persistence for debugging

### Production Considerations
- **Logging**: Comprehensive logging system with file output and console display
- **Error Handling**: Graceful failure handling with detailed error reporting
- **Monitoring**: Streamlit dashboard provides real-time system health metrics
- **Scalability**: Modular design allows for easy scaling of individual components
- **Security**: API key management through environment variables

### Key Configuration Files
- **langgraph.json**: Defines LangGraph project structure and dependencies
- **.env**: Contains API keys and environment-specific settings
- **data/*.json**: Knowledge base documents organized by support category

The system is designed to run locally for development and testing, with clear pathways for cloud deployment when needed. The modular architecture and comprehensive logging make it suitable for production environments with proper infrastructure scaling.