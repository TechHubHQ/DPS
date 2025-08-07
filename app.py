import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import init_db, get_users, get_user_submission_status, submit_poll, get_ist_date, add_user, get_poll_stats, end_poll, remove_user, is_poll_time_active, get_admin_password, update_admin_password, get_poll_end_time, extend_poll, reset_poll_time

# Initialize database
init_db()

# Initialize session state
if 'poll_active' not in st.session_state:
    st.session_state.poll_active = True

# Admin panel with session-specific authentication
admin_mode = st.sidebar.selectbox("Mode", ["User", "Admin"])

if admin_mode == "Admin":
    st.title("🔐 Admin Login")
    password = st.text_input("Enter admin password:", type="password")

    if password == get_admin_password():
        # Admin interface
        st.title("⚙️ Admin Panel")

        # Password reset section
        with st.expander("Change Admin Password"):
            new_password = st.text_input(
                "New Password:", type="password", key="new_pwd")
            confirm_password = st.text_input(
                "Confirm Password:", type="password", key="confirm_pwd")
            if st.button("Update Password"):
                if new_password and new_password == confirm_password:
                    update_admin_password(new_password)
                    st.success("Password updated successfully!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    st.error("Please enter a new password")
    elif password != "":
        st.error("Invalid password")
        st.stop()
    else:
        st.stop()

    ist_today = get_ist_date()
    today = str(ist_today)

    # Poll controls
    st.subheader("Poll Controls")
    st.write(f"**Current Poll End Time: {get_poll_end_time()}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("End Today's Poll"):
            end_poll(today)
            st.session_state.poll_active = False
            st.success("Poll ended and submissions cleared")
    with col2:
        if st.button("Reactivate Poll"):
            st.session_state.poll_active = True
            st.success("Poll reactivated")
    with col3:
        if st.button("Reset Time (6:30 PM)"):
            reset_poll_time()
            st.success("Poll time reset to 6:30 PM")

    # Poll extension
    st.write("**Extend Poll Time**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("+ 30 min"):
            new_time = extend_poll(30)
            st.success(f"Poll extended to {new_time}")
    with col2:
        if st.button("+ 1 hour"):
            new_time = extend_poll(60)
            st.success(f"Poll extended to {new_time}")
    with col3:
        if st.button("+ 1.5 hours"):
            new_time = extend_poll(90)
            st.success(f"Poll extended to {new_time}")
    with col4:
        if st.button("+ 2 hours"):
            new_time = extend_poll(120)
            st.success(f"Poll extended to {new_time}")

    # User management
    st.subheader("User Management")

    # Bulk add users
    st.write("**Bulk Add Users**")
    bulk_emp_ids = st.text_area(
        "Enter Employee IDs (comma-separated):", placeholder="1001, 1002, 1003")
    if st.button("Bulk Add Users"):
        if bulk_emp_ids.strip():
            ids = [id.strip() for id in bulk_emp_ids.split(',')]
            added = []
            errors = []
            for emp_id_str in ids:
                try:
                    emp_id = int(emp_id_str)
                    if add_user(emp_id):
                        added.append(emp_id)
                    else:
                        errors.append(f"{emp_id} (exists)")
                except ValueError:
                    errors.append(f"{emp_id_str} (invalid)")

            if added:
                st.success(f"Added: {', '.join(map(str, added))}")
            if errors:
                st.error(f"Failed: {', '.join(errors)}")
            if added:
                st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Add Single User**")
        new_emp_id = st.number_input(
            "Employee ID:", min_value=1, step=1, key="add_user")
        if st.button("Add User"):
            if add_user(new_emp_id):
                st.success(f"User {new_emp_id} added")
                st.rerun()
            else:
                st.error("Employee ID already exists")

    with col2:
        st.write("**Remove User**")
        remove_emp_id = st.number_input(
            "Employee ID:", min_value=1, step=1, key="remove_user")
        if st.button("Remove User"):
            if remove_user(remove_emp_id):
                st.success(f"User {remove_emp_id} removed")
                st.rerun()
            else:
                st.error("Employee ID not found")

    # View stats
    st.subheader("Poll Statistics")
    stats = get_poll_stats(today)

    submitted_count = sum(1 for _, status in stats if status == 1)
    total_count = len(stats)

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", total_count)
    with col2:
        st.metric("Submitted", submitted_count)
    with col3:
        st.metric("Pending", total_count - submitted_count)

    # Progress bar chart
    if total_count > 0:
        chart_data = pd.DataFrame({
            'Status': ['Submitted', 'Pending'],
            'Count': [submitted_count, total_count - submitted_count]
        })

        fig = px.bar(chart_data, x='Count', y='Status', orientation='h',
                     color='Status',
                     color_discrete_map={
                         'Submitted': '#4CAF50', 'Pending': '#FF9800'},
                     title=f"Poll Progress - {submitted_count/total_count*100:.1f}% Complete",
                     text='Count')
        fig.update_traces(textposition='inside')
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.stop()

# Regular user interface (only shown when not in admin mode)
if admin_mode == "User":
    st.title("🍽️ Dinner Polling System")
    ist_today = get_ist_date()
    st.write(f"Today's Date (IST): {ist_today}")

    # Check if poll is active (time-based and manual)
    if not is_poll_time_active():
        st.error(
            f"⏰ Today's poll has ended at {get_poll_end_time()} IST. Please check back tomorrow.")
        st.stop()
    elif not st.session_state.poll_active:
        st.error(
            "⏰ Today's poll has been ended by admin. Please check back tomorrow.")
        st.stop()

    # Get all users
    users = get_users()
    today = str(ist_today)

    # Display current status
    st.subheader("Current Status")
    submitted_users = []
    not_submitted_users = []

    for user_id, emp_id in users:
        if get_user_submission_status(user_id, today):
            submitted_users.append(emp_id)
        else:
            not_submitted_users.append(emp_id)

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Submitted: {len(submitted_users)}")
        if submitted_users:
            with st.expander("View submitted users"):
                st.write(", ".join(map(str, submitted_users)))

    with col2:
        st.error(f"❌ Pending: {len(not_submitted_users)}")
        if not_submitted_users:
            with st.expander("View pending users"):
                st.write(", ".join(map(str, not_submitted_users)))

    # Polling form
    st.subheader("Submit Your Response")
    employee_id_input = st.text_input("Enter your Employee ID:")

    if st.button("Submit Poll"):
        if employee_id_input.strip() == "":
            st.warning("Please enter your Employee ID.")
        else:
            try:
                employee_id = int(employee_id_input)
            except ValueError:
                st.error("Employee ID must be a number.")
            else:
                # Find user by emp_id
                user_found = False
                user_internal_id = None
                for uid, emp_id in users:
                    if emp_id == employee_id:
                        user_found = True
                        user_internal_id = uid
                        break

                if user_found:
                    submit_poll(user_internal_id, today)
                    st.success(
                        f"Poll submitted for Employee ID: {employee_id}!")
                    st.rerun()
                else:
                    st.error("Employee ID not found. Please check and try again.")
