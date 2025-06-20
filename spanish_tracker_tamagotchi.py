# spanish_tracker_tamagotchi.py

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
import os
import hashlib
import random

# ---------------- Config ----------------
st.set_page_config(page_title="Spanish Tracker", layout="centered")

# ---------------- Helper Functions ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_random_pet_name():
    pet_names = ["Luna", "Coco", "Pepito", "Churro", "Taco", "Nina", "Bambino", "Salsa"]
    return random.choice(pet_names)

# ---------------- Enhanced Login System ----------------
def signup_or_reset():
    st.subheader("🆕 Create Account or Reset Password")
    new_user = st.text_input("New Username", key="new_user")
    new_pass = st.text_input("New Password", type="password", key="new_pass")
    if st.button("Submit", key="signup_submit"):
        if new_user and new_pass:
            hashed_pass = hash_password(new_pass)
            lines = []
            if os.path.exists("users.txt"):
                with open("users.txt", "r") as f:
                    lines = f.readlines()
            with open("users.txt", "w") as f:
                user_found = False
                for line in lines:
                    user, _ = line.strip().split(",")
                    if user == new_user:
                        f.write(f"{new_user},{hashed_pass}\n")
                        user_found = True
                    else:
                        f.write(line)
                if not user_found:
                    f.write(f"{new_user},{hashed_pass}\n")
            st.success("Account created or password reset! Please login.")
            st.session_state.signup_mode = False
            st.experimental_rerun()
        else:
            st.error("Both fields required.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "signup_mode" not in st.session_state:
    st.session_state.signup_mode = False

if not st.session_state.authenticated:
    st.markdown("""
        <h1 style='text-align: center'>Login to Your Spanish Tracker</h1>
    """, unsafe_allow_html=True)

    if not st.session_state.signup_mode:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_clicked = st.button("Login")

        if login_clicked:
            if username and password:
                if os.path.exists("users.txt"):
                    hashed_input = hash_password(password)
                    with open("users.txt", "r") as f:
                        users = [line.strip().split(",") for line in f.readlines()]
                    if [username, hashed_input] in users:
                        st.session_state.username = username
                        st.session_state.file = f"{username}_study_log.csv"
                        st.session_state.goal_file = f"{username}_weekly_goals.csv"
                        st.session_state.authenticated = True

                        # Pet name handling
                        pet_name_file = f"{username}_pet_name.txt"
                        if os.path.exists(pet_name_file):
                            with open(pet_name_file, "r") as pf:
                                st.session_state.pet_name = pf.read().strip()
                        else:
                            new_name = get_random_pet_name()
                            with open(pet_name_file, "w") as pf:
                                pf.write(new_name)
                            st.session_state.pet_name = new_name

                        st.success(f"Welcome back, {username}!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("No users exist yet. Please create an account.")
            else:
                st.error("Please enter both a username and password")

        if st.button("Create Account or Reset Password"):
            st.session_state.signup_mode = True
            st.experimental_rerun()

        st.stop()
    else:
        signup_or_reset()
        st.stop()

# ✅ Ensure goal_file and pet_name are set if already authenticated
if "goal_file" not in st.session_state and "username" in st.session_state:
    st.session_state.goal_file = f"{st.session_state.username}_weekly_goals.csv"

if "pet_name" not in st.session_state and "username" in st.session_state:
    pet_name_file = f"{st.session_state.username}_pet_name.txt"
    if os.path.exists(pet_name_file):
        with open(pet_name_file, "r") as pf:
            st.session_state.pet_name = pf.read().strip()
    else:
        new_name = get_random_pet_name()
        with open(pet_name_file, "w") as pf:
            pf.write(new_name)
        st.session_state.pet_name = new_name

# ---------------- Tamagotchi Style Header ----------------
st.markdown("""
    <style>
    body {
        background-color: #FFF0F5;
    }
    .main {
        background-color: #FFF0F5;
        font-family: 'Comic Sans MS', cursive;
    }
    h1, h2, h3 {
        color: #FF69B4;
        text-align: center;
    }
    .tomigatchi-box {
        background-color: #FFE4E1;
        padding: 20px;
        border-radius: 25px;
        border: 4px dotted #FFB6C1;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='tomigatchi-box'>
        <h1>🐣 Meet {st.session_state.pet_name}!</h1>
        <p style='text-align: center;'>Feed your Spanish pet with study time! 🌈✨</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- Emoji Mood Tracker ----------------
st.subheader("🌤️ How are you feeling today?")
mood = st.radio("Pick your mood:", ["😊 Happy", "😫 Tired", "😎 Confident", "🤯 Overwhelmed", "😴 Sleepy"])

# ---------------- Daily Study Log Form ----------------
st.subheader("📆 Log Your Study Session")
with st.form("study_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.today())
    study_plan = st.text_area("📝 What are your study plans for today?", placeholder="E.g Practice past tense, watch Netflix with subtitles")
    task = st.text_area("📝 What did you study today?", placeholder="E.g. Practiced past tense, watched Netflix with subtitles")
    completed = st.checkbox("Task Completed")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_entry = pd.DataFrame({
            "Date": [date],
            "Task": [task],
            "Completed": [completed],
            "Mood": [mood]
        })

        try:
            existing = pd.read_csv(st.session_state.file)
            updated = pd.concat([existing, new_entry], ignore_index=True)
        except FileNotFoundError:
            updated = new_entry

        updated.to_csv(st.session_state.file, index=False)
        st.success(f"Entry saved! {st.session_state.pet_name} is happy! 🐥")

# ---------------- Weekly Goals + Visual Rewards ----------------
st.subheader("🎯 Set Your Weekly Goal")
with st.form("goal_form"):
    goal_text = st.text_input("What's your Spanish goal for this week?")
    goal_submit = st.form_submit_button("Save Goal")
    if goal_submit and goal_text:
        goal_data = pd.DataFrame({"Week": [datetime.today().isocalendar()[1]], "Goal": [goal_text]})
        try:
            goal_df = pd.read_csv(st.session_state.goal_file)
            goal_df = pd.concat([goal_df, goal_data], ignore_index=True)
        except FileNotFoundError:
            goal_df = goal_data
        goal_df.to_csv(st.session_state.goal_file, index=False)
        st.success("🎉 Goal saved! Keep it up!")

try:
    goal_df = pd.read_csv(st.session_state.goal_file)
    current_week = datetime.today().isocalendar()[1]
    weekly_goal = goal_df[goal_df["Week"] == current_week]
    if not weekly_goal.empty:
        st.markdown(f"**📌 This Week's Goal:** {weekly_goal['Goal'].values[-1]}")
except FileNotFoundError:
    pass

# ---------------- Progress Overview ----------------
st.subheader("📈 Your Progress")
try:
    df = pd.read_csv(st.session_state.file)
    st.dataframe(df, use_container_width=True)

    total_days = len(df)
    completed_days = df["Completed"].sum()
    progress = completed_days / total_days if total_days > 0 else 0
    st.progress(progress)
    st.caption(f"✅ {completed_days} of {total_days} days completed")

    # ---------------- Animated Pet Evolution ----------------
    st.subheader("🐾 Your Pet's Evolution")
    if completed_days < 3:
        pet = "🐣"
        stage = "Just Hatched!"
    elif completed_days < 7:
        pet = "🦆"
        stage = "Growing Strong!"
    elif completed_days < 14:
        pet = "🦢✨"
        stage = "Almost Fully Grown!"
    else:
        pet = "🐉😎"
        stage = "Ultimate Evolution!"

    st.markdown(f"<h1 style='text-align: center'>{pet}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center'>{stage}</h3>", unsafe_allow_html=True)

    if completed_days >= 5:
        st.success("🏆 You've reached your goal this week! Reward unlocked: 🌟 +1 Evolution Star!")

    # ---------------- Mood Trends ----------------
    st.subheader("📈 Mood Trends")
    mood_chart = df.groupby(["Mood"]).size().reset_index(name="Count")
    st.bar_chart(mood_chart.set_index("Mood"))

    # Export to Excel
    st.subheader("⬇️ Download Your Progress")
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    b64 = base64.b64encode(excel_buffer.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{st.session_state.username}_study_log.xlsx">📥 Download Excel File</a>'
    st.markdown(href, unsafe_allow_html=True)

    # ---------------- Progress Charts ----------------
    st.subheader("📊 Study Trend")
    df["Date"] = pd.to_datetime(df["Date"])
    chart_data = df.groupby(df["Date"].dt.date).size().reset_index(name="Study Sessions")
    st.line_chart(chart_data.set_index("Date"))

except FileNotFoundError:
    st.info("No entries yet. Add your first study log above!")

# ---------------- Footer ----------------
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 0.9em; color: gray;'>
    Made with 💕. Keep your Tamagotchi thriving! 🐾
    </p>
""", unsafe_allow_html=True)
