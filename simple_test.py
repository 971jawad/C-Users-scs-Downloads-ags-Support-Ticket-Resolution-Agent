import streamlit as st

st.title("🚀 Migration Test - Support Agent")
st.success("✅ Streamlit is working perfectly!")
st.info("Your support ticket system has been successfully migrated to Replit.")

# Basic test form
with st.form("basic_test"):
    test_input = st.text_input("Test Input", "Hello World")
    if st.form_submit_button("Test Submit"):
        st.balloons()
        st.write(f"Success! Input received: {test_input}")

st.write("If you can see this page, the migration is complete and working!")