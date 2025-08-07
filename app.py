import streamlit as st
import pandas as pd
from datetime import date
from database import init_db, get_users, get_user_submission_status, submit_poll, add_users_from_excel, get_ist_date

# Initialize database
init_db()

st.title("🍽️ Dinner Polling System")
ist_today = get_ist_date()
st.write(f"Today's Date (IST): {ist_today}")

# Get all users
users = get_users()
today = str(ist_today)

# Display current status
st.subheader("Current Status")
submitted_users = []
not_submitted_users = []

for user_id, name in users:
    if get_user_submission_status(user_id, today):
        submitted_users.append(name)
    else:
        not_submitted_users.append(name)

col1, col2 = st.columns(2)
with col1:
    st.success(f"✅ Submitted ({len(submitted_users)})")
    for name in submitted_users:
        st.write(f"• {name}")

with col2:
    st.error(f"❌ Not Submitted ({len(not_submitted_users)})")
    for name in not_submitted_users:
        st.write(f"• {name}")

# Upload users
st.subheader("Upload Users")
uploaded_file = st.file_uploader("Upload Excel file with user names", type=['xlsx', 'xls'])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if st.button("Add Users"):
        add_users_from_excel(df)
        st.success(f"Added {len(df)} users to database!")
        st.rerun()

# Polling form
st.subheader("Submit Your Response")
user_names = [name for _, name in users]
selected_user = st.selectbox("Select your name:", [""] + user_names)

if selected_user and st.button("Submit Poll"):
    user_id = next(uid for uid, name in users if name == selected_user)
    submit_poll(user_id, today)
    st.success(f"Poll submitted for {selected_user}!")
    st.rerun()