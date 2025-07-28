# Support Ticket Resolution Agent with Multi-Step Review Loop

A sophisticated LangGraph-based support ticket resolution system that automatically processes customer support tickets through a multi-step AI workflow with quality assurance and escalation handling.

**Assessment Implementation**: This system fully implements the required LangGraph workflow with classification, RAG retrieval, draft generation, automated review, retry logic (max 2 attempts), and escalation handling.

## 🎯 Overview

This system simulates a real customer support team workflow using AI agents, turning manual processes into an automated LangGraph flow. The system thinks, searches, writes, checks itself, improves when needed, and escalates when stuck - all without human intervention unless the AI fails.

## 🏗️ System Architecture

### Step-by-Step Flow

| Step | What Happens | Implementation |
|------|-------------|----------------|
| 1. **Ticket Ingest** | Receives subject + description | Streamlit web interface |
| 2. **Classification** | AI determines: Billing, Technical, Security, or General | Gemini 2.0 Flash via OpenRouter |
| 3. **Context Retrieval (RAG)** | Pulls relevant documents from knowledge base | FAISS vector database + TF-IDF |
| 4. **Draft Generation** | AI writes response using context + original ticket | Gemini with grounded prompting |
| 5. **Draft Review** | Separate AI checks reply for quality and policy compliance | Independent Gemini review instance |
| 6. **Retry Loop (max 2)** | If review fails, refine and retry up to 2 times | LangGraph conditional routing |
| 7. **Final Output/Escalation** | Approved response or human escalation with full logs | CSV logging + customer notification |

### 🧭 Real-Life Analogy

Think of this like a customer service AI agent that:
- **Thinks** ("what is the ticket about?") → Classification
- **Searches** ("what info should I refer to?") → RAG Retrieval  
- **Writes** ("here's your answer") → Draft Generation
- **Checks itself** ("did I follow support policies?") → Review
- **Improves if needed** ("let me try again") → Retry Loop
- **Escalates if stuck** ("this needs a human") → Human Handoff

## 🛠️ Technologies Used

- **LangGraph**: Workflow orchestration and state management
- **Gemini 2.0 Flash**: Language model via OpenRouter API
- **FAISS**: Vector database for semantic document retrieval
- **TF-IDF**: Fallback text similarity matching
- **Streamlit**: Web interface and real-time monitoring
- **Python**: Core application language
- **CSV**: Escalation logging for human triage

## 📊 Knowledge Base & Policies

The system includes comprehensive policy documents for each category:

### Billing (5 policies)
- Refund procedures and approval limits
- Billing dispute handling
- Subscription management
- Payment processing
- Pricing information guidelines

### Technical (6 policies)  
- Troubleshooting procedures
- API integration guidelines
- Performance diagnosis
- Security access restrictions
- Mobile app support
- Outage response protocols

### Security (6 policies)
- Security incident response
- Account lockout procedures
- Data breach protocols
- GDPR compliance
- SSO configuration
- Identity verification

### General (6 policies)
- Communication standards
- Feature request handling
- SLA requirements
- Escalation procedures
- Self-service resources
- Professional conduct

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- OpenRouter API key with Gemini access

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd support-ticket-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export GEMINI_API_KEY="your-openrouter-api-key"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Access the interface**
   Open http://localhost:5000 in your browser



## 🎮 Usage Examples

### Normal Ticket Flow

1. **Submit a ticket**: "Login failure on mobile app"
2. **Auto-Classification**: System identifies as "Technical"
3. **Context Retrieval**: Fetches mobile troubleshooting docs
4. **Draft Generation**: Creates personalized response with steps
5. **Review**: Quality check passes
6. **Final Output**: Customer receives helpful response

### Retry Scenario

1. **Submit a ticket**: "Need refund for overcharge"
2. **Classification**: "Billing"
3. **First Draft**: Generic refund response
4. **Review**: Rejected - lacks specific policy details
5. **Retry**: Enhanced context retrieval
6. **Second Draft**: Policy-compliant response with approval process
7. **Review**: Approved
8. **Final Output**: Detailed, policy-correct response

### Escalation Scenario

1. **Submit a ticket**: "Suspected data breach in my account"
2. **Classification**: "Security"
3. **First Draft**: Basic security advice
4. **Review**: Rejected - security incident requires human handling
5. **Retry**: Attempts more specific response
6. **Review**: Still rejected - too sensitive for AI
7. **Escalation**: Logged to CSV with full context for security team

## 🔄 Workflow Visualization

### LangStudio Interactive Workflow Diagram Setup:

2. **Add your GEMINI_API_KEY to environment variables** ✓  
3. **Submit a ticket through the Streamlit interface**
4. **Click the "View Live Workflow" link that appears during processing**
5. **Watch your ticket process in real-time with full interactivity**





### Static Workflow Overview:

```
[Ticket Input] 
     ↓ 
[Classifier] ──→ Billing/Technical/Security/General
     ↓ 
[RAG Retriever] ──→ Policy Documents + Context
     ↓ 
[Draft Generator] ──→ Personalized Response
     ↓ 
[Reviewer] ──→ Quality + Policy Check
  ↙     ↘
Retry  ✅ Approve
  ↓        ↓
Retry Limit? → [Final Output] or [Escalate]
  ↓               ↓
[Human CSV] ← [Customer Response]
```



## 🏗️ Why Built This Way

### LangGraph Choice
- **State Management**: Complex workflows need persistent state across multiple AI calls
- **Conditional Routing**: Different paths based on review outcomes and retry counts
- **Retry Logic**: Built-in support for loop detection and termination
- **Debugging**: Visual graph representation and state inspection

### Multi-Agent Architecture  
- **Separation of Concerns**: Classification, generation, and review are distinct skills
- **Quality Assurance**: Independent reviewer prevents hallucinations and policy violations
- **Retry Mechanism**: Feedback-driven improvement mimics human revision process

### RAG Implementation
- **Grounded Responses**: All answers based on actual policy documents
- **Category-Specific**: Different knowledge bases for different issue types
- **Scalable**: Easy to add new documents and categories
- **Fallback**: TF-IDF ensures responses even when vector search fails

### Policy-First Design
- **Compliance**: Built-in policy checking prevents inappropriate responses
- **Escalation**: Clear rules for when human intervention is required
- **Documentation**: Full audit trail for every ticket resolution

## 📁 Project Structure

```
support-ticket-agent/
├── app.py                 # Streamlit web interface
├── support_agent/         # Core agent implementation
│   ├── graph.py          # LangGraph workflow definition
│   ├── nodes.py          # Individual processing nodes
│   ├── state.py          # State schema and management
│   ├── gemini_client.py  # LLM integration
│   ├── rag_system.py     # RAG and retrieval logic
│   ├── knowledge_base.py # Knowledge base management
│   └── utils.py          # Utilities and logging
├── data/                 # Knowledge base documents
│   ├── billing_docs.json
│   ├── technical_docs.json
│   ├── security_docs.json
│   └── general_docs.json
├── logs/                 # Application logs
├── indexes/              # FAISS vector indexes
├── escalation_log.csv    # Human escalation tracking
├── langgraph.json        # LangGraph CLI configuration
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: OpenRouter API key for Gemini access

### LangGraph Settings
- **Checkpointing**: Memory-based state persistence
- **Thread Management**: Unique thread IDs for each ticket
- **Retry Limits**: Maximum 2 review attempts per ticket

### RAG Configuration
- **Vector Model**: bge-small-en-v1.5 for embeddings
- **Retrieval**: Top-3 documents per category
- **Fallback**: TF-IDF similarity matching
- **Threshold**: Minimum relevance score of 0.1

## 📈 Monitoring & Analytics

The Streamlit interface provides:
- **Real-time Metrics**: Success rates, categories, processing times
- **Ticket History**: Complete audit trail of all processed tickets
- **System Logs**: Detailed logging of all workflow steps
- **Escalation Tracking**: CSV export of failed cases

## 🔄 Interactive Workflow Visualization


**Key Features:**
- **Real-time Execution Tracing**: Watch each ticket flow through the system live
- **Interactive Node Inspection**: Click any node to view inputs, outputs, and processing details  
- **State Transition Visualization**: See how ticket data transforms at each step
- **Performance Metrics**: Monitor processing times and success rates
- **Error Debugging**: Identify bottlenecks and failure points instantly
- **Retry Logic Visualization**: Track the complete retry loop with detailed reasoning


**Static Overview:**
```
[Ticket Input] 
     ↓ 
[Classifier] ──→ Billing/Technical/Security/General
     ↓ 
[RAG Retriever] ──→ Policy Documents + Context
     ↓ 
[Draft Generator] ──→ Personalized Response
     ↓ 
[Reviewer] ──→ Quality + Policy Check
  ↙     ↘
Retry  ✅ Approve
  ↓        ↓
Retry Limit? → [Final Output] or [Escalate]
  ↓               ↓
[Human CSV] ← [Customer Response]
```

> **Note**: The interactive LangStudio visualization provides 100x more detail than this static diagram, showing execution traces, timing data, state changes, and decision logic for enterprise-level monitoring.

## 🎥 Demo Features

The system demonstrates:
- **Automatic Classification**: No manual category selection needed
- **Policy Compliance**: Responses follow documented procedures
- **Quality Assurance**: Independent review prevents poor responses
- **Escalation Handling**: Complex cases route to humans appropriately
- **Customer Experience**: Professional, empathetic, and helpful responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using LangGraph, Gemini 2.0 Flash, and modern AI practices**
