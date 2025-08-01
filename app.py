import streamlit as st
from groq_helper import get_groq_response
from utils import load_memory, save_memory

# --- Streamlit Page Setup ---
st.set_page_config(page_title="💰 Financial Assistant", layout="wide")
st.title("🤖 Financial Assistant using GroqCloud")
st.markdown("Manage SIPs, taxes, and financial goals with long-term memory & multi-model LLMs.")

# --- Sidebar: Configuration ---
st.sidebar.title("⚙️ Settings")

groq_api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")

# Model selector
# Model selector (Updated: Removed decommissioned model)
model = st.sidebar.selectbox("Choose LLM Model", options=[
    "qwen/qwen3-32b",
    "llama3-70b-8192",
    "gemma-7b-it"
], index=0)

if model == "mixtral-8x7b-32768":
    st.warning("❌ This model is no longer supported by Groq. Please choose another one.")

st.sidebar.markdown(f"**Current Model:** `{model}`")

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

# --- Load memory ---
memory = load_memory()

# --- Display chat history ---
for msg in memory:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input ---
user_input = st.chat_input("Ask something like 'Remind me about SIP on 5th' or 'How much tax did I pay last year?'")

if user_input and groq_api_key:
    # Show user message
    st.chat_message("user").markdown(user_input)
    memory.append({"role": "user", "content": user_input})

    # LLM response
    with st.spinner("Thinking..."):
        reply = get_groq_response(
            api_key=groq_api_key,
            model=model,
            messages=memory,
            temperature=temperature
        )

    st.chat_message("assistant").markdown(reply)
    memory.append({"role": "assistant", "content": reply})

    # Save conversation
    save_memory(memory)
