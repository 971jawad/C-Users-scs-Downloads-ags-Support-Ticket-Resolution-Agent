import streamlit as st

st.title("Working Streamlit App")
st.write("This should display without issues")

if st.button("Test Button"):
    st.success("Button works!")