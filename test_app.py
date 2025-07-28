import streamlit as st
import os

st.set_page_config(
    page_title="Support Agent Test",
    page_icon="🎫",
    layout="wide"
)

st.title("🎫 Support Ticket Agent - System Status")

# Test environment
st.header("Environment Check")
gemini_key = os.environ.get("GEMINI_API_KEY")
st.write(f"✅ Gemini API Key: {'Configured' if gemini_key else '❌ Missing'}")

# Test basic form
st.header("Test Ticket Submission")
with st.form("test_ticket"):
    subject = st.text_input("Subject", value="Test billing issue")
    description = st.text_area("Description", value="I need help with my billing")
    submitted = st.form_submit_button("Submit Test Ticket")
    
    if submitted:
        st.success("✅ Form submission works!")
        st.write(f"Subject: {subject}")
        st.write(f"Description: {description}")

# Test imports
st.header("System Components")
try:
    from support_agent.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    st.write("✅ Knowledge Base: Loaded")
    stats = kb.get_stats()
    st.write(f"Documents loaded: {stats}")
except Exception as e:
    st.error(f"❌ Knowledge Base: {e}")

try:
    from support_agent.rag_system import RAGSystem
    rag = RAGSystem()
    st.write("✅ RAG System: Loaded")
    category_stats = rag.get_category_stats()
    st.write(f"RAG Stats: {category_stats}")
except Exception as e:
    st.error(f"❌ RAG System: {e}")

try:
    from support_agent.gemini_client import GeminiClient
    if gemini_key:
        client = GeminiClient()
        st.write("✅ Gemini Client: Connected")
    else:
        st.warning("⚠️ Gemini Client: API key missing")
except Exception as e:
    st.error(f"❌ Gemini Client: {e}")

st.success("🎉 Basic system test complete!")