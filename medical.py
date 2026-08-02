import streamlit as st
from openai import OpenAI
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Medical Booking", page_icon="🏥", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🏥 AI Doctor Booking System")

# --------------------------
# Session State Initialization
# --------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "messages" not in st.session_state:
    st.session_state.messages = []

if "count" not in st.session_state:
    st.session_state.count = 0

if "patient" not in st.session_state:
    st.session_state.patient = {}

# --------------------------
# Step 1: Patient Registration
# --------------------------
if st.session_state.step == 1:
    st.header("Step 1: Patient Details")

    with st.form("patient_form"):
        name = st.text_input("Name", placeholder="Enter full name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=1, max_value=100, value=25)
        disease = st.text_input("Main Problem / Symptoms", placeholder="e.g., Fever, Knee Pain")
        
        room = st.radio("Room Type Preference", ["AC", "Non AC", "Less Queue"], horizontal=True)
        budget = st.selectbox("Budget Range (₹)", ["1000-2000", "2000-3000", "3000-4000"])

        hospital = st.selectbox("Select Hospital", ["Apollo", "Fortis", "Max Hospital"])
        
        doctors = {
            "Apollo": ["Dr. Sharma (Cardiology)", "Dr. Sneha (General)"],
            "Fortis": ["Dr. Amit (Orthopedic)", "Dr. Riya (Neurology)"],
            "Max Hospital": ["Dr. Raj (Pediatrics)", "Dr. Neha (Dermatology)"]
        }

        doctor = st.selectbox("Select Doctor", doctors[hospital])
        
        submitted = st.form_submit_button("Continue to Medical Chat")

    if submitted:
        if not name.strip() or not disease.strip():
            st.error("Please fill in both Name and Main Problem to proceed.")
        else:
            st.session_state.patient = {
                "name": name,
                "gender": gender,
                "age": age,
                "disease": disease,
                "room": room,
                "budget": budget,
                "hospital": hospital,
                "doctor": doctor
            }

            st.session_state.messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and polite medical assistant. "
                        "Ask ONLY 4 targeted questions sequentially to understand the patient's issue better:\n"
                        "1. Since when are you facing this issue?\n"
                        "2. Any previous disease or medical history?\n"
                        "3. Current medicines being taken?\n"
                        "4. Any known allergies?\n"
                        "Ask one short question at a time. After four questions, inform the user they can book an appointment."
                    )
                }
            ]
            st.session_state.step = 2
            st.rerun()

# --------------------------
# Step 2: AI Medical Chat
# --------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Interactive Assessment")

    # Display Sidebar Patient Info
    with st.sidebar:
        st.subheader("Patient Summary")
        for key, val in st.session_state.patient.items():
            st.write(f"**{key.capitalize()}:** {val}")

    # Render previous messages (excluding system prompt)
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"]):
                st.write(m["content"])

    # Determine dynamic placeholder text based on turn count
    if st.session_state.count == 0:
        placeholder_text = "Say Hi"
    elif st.session_state.count >= 3:
        placeholder_text = "add more details / get consultancy"
    else:
        placeholder_text = "Type your response..."

    prompt = st.chat_input(placeholder_text)

    if prompt:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI Chat API
        with st.spinner("AI Doctor is thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content

        # Append Assistant Message
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.count += 1
        st.rerun()

    # Show booking button after 3-4 interactions
    if st.session_state.count >= 3:
        st.divider()
        st.info("You have shared enough details. You can now finalize your appointment.")
        if st.button("Proceed to Book Appointment", type="primary"):
            st.session_state.step = 3
            st.rerun()

# --------------------------
# Step 3: Appointment Confirmation & Summary
# --------------------------
else:
    st.header("Step 3: Booking Confirmation")

    patient = st.session_state.patient
    appointment_date = datetime.now() + timedelta(days=2)

    with st.spinner("Generating medical summary and appointment..."):
        summary_prompt = f"""
        Patient Details:
        {patient}

        Chat History:
        {st.session_state.messages}

        Please generate a well-structured response with the following markdown headers:
        ### 📋 Disease Summary
        ### 💡 Health Suggestions
        ### 🏠 Safe Home Remedies
        ### ⚠️ Medical Disclaimer
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}]
        )

        summary = response.choices[0].message.content

    st.success("🎉 Appointment Booked Successfully!")

    # Display Appointment Details in columns
    st.markdown("### 🏥 Appointment Voucher")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Appointment ID:** `{random.randint(10000, 99999)}`")
        st.write(f"**Patient Name:** {patient['name']}")
        st.write(f"**Hospital:** {patient['hospital']}")
        st.write(f"**Doctor:** {patient['doctor']}")
    with col2:
        st.write(f"**Room Preference:** {patient['room']}")
        st.write(f"**Date:** {appointment_date.strftime('%d %B %Y')}")
        st.write(f"**Time Slot:** 10:30 AM")
        st.write(f"**Budget:** ₹{patient['budget']}")

    st.divider()

    # Display Medical Summary
    st.write(summary)

    st.divider()
    if st.button("Book Another Appointment"):
        st.session_state.step = 1
        st.session_state.count = 0
        st.session_state.messages = []
        st.session_state.patient = {}
        st.rerun()