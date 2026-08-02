import streamlit as st
from openai import OpenAI
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Medical Booking", page_icon="🏥")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🏥 AI Doctor Booking System")

# --------------------------
# Session State
# --------------------------

if "step" not in st.session_state:
    st.session_state.step = 1

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------
# Step 1
# --------------------------

if st.session_state.step == 1:

    st.header("Patient Details")

    name = st.text_input("Name")

    gender = st.selectbox(
        "Gender",
        ["Male","Female","Other"]
    )

    age = st.number_input(
        "Age",
        1,
        100
    )

    disease = st.text_input(
        "Main Problem"
    )

    room = st.radio(
        "Room Type",
        ["AC","Non AC","Less Queue"]
    )

    budget = st.selectbox(
        "Budget",
        [
            "1000-2000",
            "2000-3000",
            "3000-4000"
        ]
    )

    hospital = st.selectbox(
        "Hospital",
        [
            "Apollo",
            "Fortis",
            "Max Hospital"
        ]
    )

    doctors = {
        "Apollo":["Dr Sharma","Dr Sneha"],
        "Fortis":["Dr Amit","Dr Riya"],
        "Max Hospital":["Dr Raj","Dr Neha"]
    }

    doctor = st.selectbox(
        "Doctor",
        doctors[hospital]
    )

    if st.button("Continue"):

        st.session_state.patient = {
            "name":name,
            "gender":gender,
            "age":age,
            "disease":disease,
            "room":room,
            "budget":budget,
            "hospital":hospital,
            "doctor":doctor
        }

        st.session_state.messages = [{
            "role":"system",
            "content":"""
You are a medical assistant.

Ask ONLY 4 questions.

1. Since when are you facing this issue?

2. Any previous disease?

3. Current medicines?

4. Any allergy?

After four questions stop.
"""
        }]

        st.session_state.step = 2
        st.rerun()

# --------------------------
# Step 2
# --------------------------

elif st.session_state.step == 2:

    st.header("Medical Chat")

    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if "count" not in st.session_state:
        st.session_state.count = 0

    prompt = st.chat_input("Answer")

    if prompt:

        st.session_state.messages.append(
            {
                "role":"user",
                "content":prompt
            }
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append(
            {
                "role":"assistant",
                "content":reply
            }
        )

        st.session_state.count += 1

        st.rerun()

    if st.session_state.count >= 4:

        if st.button("Book Appointment"):

            st.session_state.step = 3
            st.rerun()

# --------------------------
# Step 3
# --------------------------

else:

    patient = st.session_state.patient

    appointment = datetime.now() + timedelta(days=2)

    summary_prompt = f"""
Patient Details

{patient}

Conversation

{st.session_state.messages}

Generate

1. Disease Summary

2. Suggestions

3. Home Remedy

4. Disclaimer
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role":"user",
                "content":summary_prompt
            }
        ]
    )

    summary = response.choices[0].message.content

    st.success("Appointment Booked")

    st.write("### Appointment Details")

    st.write("Appointment ID:", random.randint(10000,99999))

    st.write("Hospital:", patient["hospital"])

    st.write("Doctor:", patient["doctor"])

    st.write("Room:", patient["room"])

    st.write("Date:", appointment.strftime("%d %B %Y"))

    st.write("Time:", "10:30 AM")

    st.divider()

    st.write(summary)