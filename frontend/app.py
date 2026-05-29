import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Herramienta Electoral")

if st.button("Health check"):
    response = requests.get(f"{API_URL}/health", timeout=10)
    st.json(response.json())
