# app.py
import streamlit as st
from groq_helper import get_groq_response
from utils import load_memory, save_memory, calculate_sip, sync_chat_to_firebase, sync_emi_to_firebase, sync_emi_to_firebase, calculate_emi
import re
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# --- Page Setup ---
st.set_page_config(page_title="💰 Financial Assistant", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 Financial Assistant using GroqCloud</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Manage SIPs, EMIs, taxes, reminders, and financial goals with Groq LLMs + long-term memory.</p>", unsafe_allow_html=True)
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")


    model = st.selectbox("🧠 Choose Groq Model", options=[
        "qwen/qwen3-32b",
        "llama3-70b-8192",
        "gemma-7b-it"
    ], index=0)

    temperature = st.slider("🎯 Response Creativity (temperature)", 0.0, 1.0, 0.7, 0.05)

    st.markdown(f"**Current Model:** `{model}`")

    if model == "mixtral-8x7b-32768":
        st.warning("❌ This model is no longer supported by Groq. Please choose another one.")

# --- Memory Management ---
memory = load_memory()

# --- Layout: Two Columns ---
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("💬 Chat History")

    for msg in memory:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type here...")

    if user_input and groq_api_key:
        st.chat_message("user").markdown(user_input)
        memory.append({"role": "user", "content": user_input})

        # --- Detect SIP calculation intent ---
        sip_match = re.search(r'₹?(\d+)[^\d]+per\s+(month|monthly)[^\d]+(\d+)\s+year', user_input.lower())
        if sip_match:
            monthly, _, years = sip_match.groups()
            monthly = int(monthly)
            years = int(years)
            result = calculate_sip(monthly, years)
            reply = f"📈 If you invest ₹{monthly}/month for {years} years, you'll have approximately **₹{result}** at 12% annual return (compounded monthly)."
        else:
            # --- LLM Response ---
            with st.spinner("💭 Thinking..."):
                reply = get_groq_response(
                    api_key=groq_api_key,
                    model=model,
                    messages=memory,
                    temperature=temperature
                )

        st.chat_message("assistant").markdown(reply)
        memory.append({"role": "assistant", "content": reply})
        save_memory(memory)

        # Sync memory to Firebase (New Feature)
        sync_chat_to_firebase(memory)

with right_col:
    st.subheader("📊 Financial Tools")

    with st.expander("📈 SIP Calculator"):
        st.markdown("Calculate how your monthly investments grow over time.")

        monthly = st.number_input("Monthly Investment (₹)", min_value=100, step=100, value=1000)
        years = st.number_input("Investment Duration (Years)", min_value=1, step=1, value=5)
        rate = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=20.0, step=0.5, value=12.0)

        if st.button("📊 Calculate SIP"):
            result = calculate_sip(monthly, years, rate / 100)
            st.success(f"📈 After {years} years, your ₹{monthly}/month SIP will grow to approximately ₹{result}.")

    with st.expander("📆 EMI Calculator"):
        st.markdown("Calculate your monthly loan EMI based on amount, rate, and tenure.")

        principal = st.number_input("🏦 Loan Amount (₹)", min_value=1000.0, step=1000.0)
        tenure_years = st.slider("🗕️ Tenure (Years)", 1, 30, 5)
        annual_rate = st.slider("💰 Interest Rate (Annual %)", 1.0, 20.0, 10.0)

        if st.button("🧲 Calculate EMI"):
            from utils import calculate_emi
            emi, total_payment, total_interest = calculate_emi(principal, annual_rate, tenure_years)

            st.success(f"💸 **EMI**: ₹{emi:,.2f} / month")
            st.info(f"📋 **Total Payment** over {tenure_years} years: ₹{total_payment:,.2f}")
            st.warning(f"📉 **Total Interest Paid**: ₹{total_interest:,.2f}")

    with st.expander("🎯 Goal Tracker (Cloud Synced)"):
        st.markdown("Set financial goals and track your savings progress over time.")

        from utils import load_goals, add_goal, update_goal

        with st.form("add_goal_form"):
            name = st.text_input("🎯 Goal Name", placeholder="e.g., Travel Fund")
            target = st.number_input("💰 Target Amount (₹)", min_value=100.0, step=100.0)
            duration = st.slider("🗓️ Duration (months)", 1, 60, 12)
            submitted = st.form_submit_button("➕ Add Goal")
            if submitted and name and target:
                add_goal(name, target, duration)
                st.success(f"✅ Added goal: {name}")

        st.markdown("### 📋 Your Synced Goals")
        goals = load_goals()
        if goals:
            for goal in goals:
                st.markdown(f"**{goal['name']}** (Target: ₹{goal['target']:,.0f}, Saved: ₹{goal['saved']:,.0f})")
                progress = min(goal["saved"] / goal["target"], 1.0)
                st.progress(progress, text=f"{int(progress*100)}% complete")

                new_val = st.number_input(f"💼 Update '{goal['name']}' Saved", 
                                          min_value=0.0,
                                          key=f"{goal['id']}_input", 
                                          value=float(goal['saved']))

                if st.button(f"Update Goal", key=f"{goal['id']}_update"):
                    update_goal(goal['id'], new_val)
                    st.success(f"Updated '{goal['name']}'")
        else:
            st.info("No cloud goals found. Add one above.")

    with st.expander("🧠 Memory Viewer"):
        st.code(memory, language="json")