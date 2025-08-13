from datetime import datetime
import pytz
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from database import (
    init_db, get_users, get_user_submission_status, submit_poll, get_ist_date, add_user,
    get_poll_stats, end_poll, remove_user, is_poll_time_active, get_admin_password,
    update_admin_password, get_poll_end_time, extend_poll, reset_poll_time,
    is_poll_manually_ended, set_poll_manually_ended, bulk_add_users, reset_poll_submissions,
    reset_user_submission, get_poll_history, get_user_submission_history, export_poll_data,
    get_admin_dashboard_stats, get_user_by_emp_id
)
from alembic.config import Config
from alembic import command
import time


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

# Page configuration
st.set_page_config(
    page_title="Dinner Polling System",
    page_icon="polling.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load custom CSS
def load_css():
    try:
        with open('static/css/modern_style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline CSS if file not found - simplified version
        st.markdown(
            """
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
                
                /* Basic container fixes */
                .main .block-container {
                    padding-top: 2rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                    max-width: 100%;
                    width: 100%;
                    font-family: 'Inter', sans-serif;
                }
                
                /* Ensure full width utilization */
                .stApp {
                    max-width: 100%;
                }
                
                .element-container {
                    width: 100%;
                }
                
                /* Basic responsive design */
                @media (max-width: 768px) {
                    .main .block-container {
                        padding-left: 0.5rem;
                        padding-right: 0.5rem;
                    }
                }
                </style>
            """, unsafe_allow_html=True
        )


# Initialize database
init_db()

# Load CSS styles
load_css()

# Initialize session state
if 'poll_active' not in st.session_state:
    st.session_state.poll_active = True
if 'last_timer_update' not in st.session_state:
    st.session_state.last_timer_update = time.time()

# Helper function to get timer info


def get_timer_info():
    ist_tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist_tz)
    poll_end_time_str = get_poll_end_time()
    poll_end_time = datetime.strptime(poll_end_time_str, '%H:%M').time()
    poll_end_datetime = datetime.combine(current_time.date(), poll_end_time)
    poll_end_datetime = ist_tz.localize(poll_end_datetime)
    time_remaining = poll_end_datetime - current_time
    total_seconds = int(time_remaining.total_seconds())

    if total_seconds > 0:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return hours, minutes, seconds, total_seconds, False
    else:
        return 0, 0, 0, 0, True


# Admin panel with session-specific authentication
admin_mode = st.sidebar.selectbox(
    "🔧 Mode", ["User", "Admin"], help="Switch between User and Admin modes"
)

if admin_mode == "Admin":
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.title("🔐 Admin Login")
    password = st.text_input("Enter admin password:", type="password",
                             help="Enter the admin password to access the control panel")
    if password == get_admin_password():
        # Admin interface
        st.title("⚙️ Admin Control Panel")
        st.markdown("---")
        # Password reset section
        with st.expander("🔑 Change Admin Password", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input(
                    "New Password:", type="password", key="new_pwd")
            with col2:
                confirm_password = st.text_input(
                    "Confirm Password:", type="password", key="confirm_pwd")
            if st.button("🔄 Update Password", key="update_pwd"):
                if new_password and new_password == confirm_password:
                    update_admin_password(new_password)
                    st.success("✅ Password updated successfully!")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    st.error("❌ Please enter a new password")

        ist_today = get_ist_date()
        today = str(ist_today)

        # Enhanced Admin Dashboard Stats
        st.subheader("📈 Admin Dashboard Overview")
        dashboard_stats = get_admin_dashboard_stats()

        # Enhanced metrics display with responsive admin cards
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(
                f"""
                <div class="admin-metric-card">
                    <div class="metric-value" style="color: #667eea;">{dashboard_stats['total_users']}</div>
                    <div class="metric-label">Total Users</div>
                </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"""
                <div class="admin-metric-card">
                    <div class="metric-value" style="color: #28a745;">{dashboard_stats['today_submissions']}</div>
                    <div class="metric-label">Today's Submissions</div>
                </div>
                """, unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"""
                <div class="admin-metric-card">
                    <div class="metric-value" style="color: #17a2b8;">{dashboard_stats['total_submissions']}</div>
                    <div class="metric-label">Total Submissions</div>
                </div>
                """, unsafe_allow_html=True)
        with col4:
            st.markdown(
                f"""
                <div class="admin-metric-card">
                    <div class="metric-value" style="color: #ffc107;">{dashboard_stats['active_days']}</div>
                    <div class="metric-label">Active Days</div>
                </div>
                """, unsafe_allow_html=True)
        with col5:
            st.markdown(
                f"""
                <div class="admin-metric-card">
                    <div class="metric-value" style="color: #6f42c1;">{dashboard_stats['avg_participation']}</div>
                    <div class="metric-label">Avg Daily Participation</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Poll controls
        st.subheader("📊 Poll Controls")
        hours, minutes, seconds, total_seconds, ended = get_timer_info()
        if not ended:
            st.info(
                f"⏰ **Current Poll End Time: {get_poll_end_time()} IST** | Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            st.warning(f"⏰ **Poll Ended at: {get_poll_end_time()} IST**")

        # Enhanced poll control buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🛑 End Today's Poll", key="end_poll", help="End poll and clear all submissions"):
                end_poll(today)
                st.success("✅ Poll ended and submissions cleared")
                st.rerun()
        with col2:
            if st.button("🔄 Reset Poll", key="reset_poll", help="Reset all submissions and reactivate poll"):
                if reset_poll_submissions(today):
                    st.success(
                        "✅ Poll reset successfully - all submissions cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to reset poll")
        with col3:
            if st.button("🔄 Reactivate Poll", key="reactivate_poll", help="Reactivate poll without clearing submissions"):
                set_poll_manually_ended(False)
                st.success("✅ Poll reactivated")
                st.rerun()
        with col4:
            if st.button("⏰ Reset Time (6:30 PM)", key="reset_time", help="Reset poll end time to default"):
                reset_poll_time()
                st.success("✅ Poll time reset to 6:30 PM")
                st.rerun()

        # Poll extension
        st.subheader("⏱️ Extend Poll Time")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⏰ + 30 min", key="extend_30"):
                new_time = extend_poll(30)
                st.success(f"✅ Poll extended to {new_time}")
                st.rerun()
        with col2:
            if st.button("⏰ + 1 hour", key="extend_60"):
                new_time = extend_poll(60)
                st.success(f"✅ Poll extended to {new_time}")
                st.rerun()
        with col3:
            if st.button("⏰ + 1.5 hours", key="extend_90"):
                new_time = extend_poll(90)
                st.success(f"✅ Poll extended to {new_time}")
                st.rerun()
        with col4:
            if st.button("⏰ + 2 hours", key="extend_120"):
                new_time = extend_poll(120)
                st.success(f"✅ Poll extended to {new_time}")
                st.rerun()
        st.markdown("---")

        # User management
        st.subheader("👥 User Management")
        # Bulk add users
        with st.expander("📝 Bulk Add Users", expanded=False):
            st.markdown(
                "**Format:** `Employee_ID:Employee_Name`, one per line or comma-separated")
            bulk_users_input = st.text_area("Enter Employee Data:", placeholder="1001:John Doe\n1002:Jane Smith\nOR 1001:John Doe, 1002:Jane Smith",
                                            height=100, help="Enter employee data in the format ID:Name")
            if st.button("📥 Bulk Add Users", key="bulk_add"):
                if bulk_users_input.strip():
                    # Parse input - handle both newline and comma separation
                    lines = bulk_users_input.replace(',', ' ').split(' ')
                    user_data = []
                    parse_errors = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if ':' in line:
                            try:
                                emp_id_str, emp_name = line.split(':', 1)
                                emp_id = int(emp_id_str.strip())
                                emp_name = emp_name.strip()
                                if emp_name:
                                    user_data.append((emp_id, emp_name))
                                else:
                                    parse_errors.append(f"{line} (empty name)")
                            except ValueError:
                                parse_errors.append(f"{line} (invalid format)")
                        else:
                            parse_errors.append(
                                f"{line} (missing ':' separator)")
                    if parse_errors:
                        st.error(f"❌ Format errors: {', '.join(parse_errors)}")
                    if user_data:
                        added, errors = bulk_add_users(user_data)
                        if added:
                            added_display = [
                                f"{emp_id}:{name}" for emp_id, name in added]
                            st.success(f"✅ Added: {', '.join(added_display)}")
                        if errors:
                            st.error(f"❌ Failed: {', '.join(errors)}")
                        if added:
                            st.rerun()

        # Additional Admin Features
        st.markdown("---")
        st.subheader("📈 Advanced Admin Features")

        # Poll History and Analytics
        with st.expander("📉 Poll History & Analytics", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📅 Recent Poll History**")
                history = get_poll_history(7)
                if history:
                    history_df = pd.DataFrame(
                        history, columns=['Date', 'Submissions'])
                    st.dataframe(
                        history_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No poll history available")

            with col2:
                st.markdown("**📊 User Lookup**")
                lookup_emp_id = st.number_input(
                    "Employee ID for History:", min_value=1, step=1, key="lookup_user")
                if st.button("🔍 Lookup User History", key="lookup_history"):
                    user_history = get_user_submission_history(
                        lookup_emp_id, 10)
                    if user_history:
                        user_df = pd.DataFrame(user_history, columns=[
                                               'Date', 'Submitted'])
                        user_df['Status'] = user_df['Submitted'].apply(
                            lambda x: '✅ Yes' if x else '❌ No')
                        st.dataframe(
                            user_df[['Date', 'Status']], use_container_width=True, hide_index=True)
                    else:
                        st.warning("No history found for this user")

        # Data Export
        with st.expander("💾 Data Export & Management", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📊 Export Today's Data**")
                if st.button("💾 Export Today's Poll Data", key="export_today"):
                    export_data = export_poll_data(today)
                    if export_data:
                        export_df = pd.DataFrame(export_data, columns=[
                                                 'Employee ID', 'Employee Name', 'Submitted'])
                        export_df['Status'] = export_df['Submitted'].apply(
                            lambda x: 'Submitted' if x else 'Pending')
                        csv = export_df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv,
                            file_name=f"poll_data_{today}.csv",
                            mime="text/csv"
                        )
                        st.success(f"✅ Data exported for {today}")
                    else:
                        st.warning("No data to export")

            with col2:
                st.markdown("**🗑️ Individual User Reset**")
                reset_emp_id = st.number_input(
                    "Employee ID to Reset:", min_value=1, step=1, key="reset_user_id")
                if st.button("🔄 Reset User Submission", key="reset_individual_user"):
                    user_info = get_user_by_emp_id(reset_emp_id)
                    if user_info:
                        if reset_user_submission(user_info['id'], today):
                            st.success(
                                f"✅ Reset submission for {user_info['emp_name']} (ID: {reset_emp_id})")
                            st.rerun()
                        else:
                            st.warning(
                                f"No submission found for {user_info['emp_name']} today")
                    else:
                        st.error("❌ Employee ID not found")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown("**➕ Add Single User**")
                new_emp_id = st.number_input(
                    "Employee ID:", min_value=1, step=1, key="add_user")
                new_emp_name = st.text_input(
                    "Employee Name:", key="add_user_name")
                if st.button("➕ Add User", key="add_single_user"):
                    if new_emp_name.strip():
                        if add_user(new_emp_id, new_emp_name.strip()):
                            st.success(
                                f"✅ User {new_emp_id}:{new_emp_name} added")
                            st.rerun()
                        else:
                            st.error("❌ Employee ID already exists")
                    else:
                        st.error("❌ Please enter employee name")
        with col2:
            with st.container():
                st.markdown("**➖ Remove User**")
                remove_emp_id = st.number_input(
                    "Employee ID:", min_value=1, step=1, key="remove_user")
                if st.button("🗑️ Remove User", key="remove_single_user"):
                    if remove_user(remove_emp_id):
                        st.success(f"✅ User {remove_emp_id} removed")
                        st.rerun()
                    else:
                        st.error("❌ Employee ID not found")
            st.markdown("---")

        # View stats
        st.subheader("📈 Poll Statistics")
        stats = get_poll_stats(today)
        submitted_count = sum(1 for _, _, status in stats if status == 1)
        total_count = len(stats)
        pending_count = total_count - submitted_count
        completion_rate = (submitted_count / total_count *
                           100) if total_count > 0 else 0

        # Enhanced Metrics with modern cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class="status-card">
                    <div class="metric-value" style="color: #667eea;">{total_count}</div>
                    <div class="metric-label">Total Users</div>
                </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"""
                <div class="status-card success">
                    <div class="metric-value" style="color: #28a745;">{submitted_count}</div>
                    <div class="metric-label">Submitted</div>
                </div>     """, unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"""
                <div class="status-card danger">
                    <div class="metric-value" style="color: #dc3545;">{pending_count}</div>
                    <div class="metric-label">Pending</div>
                </div>     """, unsafe_allow_html=True)
        with col4:
            st.markdown(
                f"""
                <div class="status-card">
                    <div class="metric-value" style="color: #17a2b8;">{completion_rate:.1f}%</div>
                    <div class="metric-label">Complete</div>
                </div>
                """, unsafe_allow_html=True)

        # Enhanced Progress visualization
        if total_count > 0:
            # Create a modern donut chart
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=['Submitted', 'Pending'],
                        values=[submitted_count, pending_count],
                        hole=.6,
                        marker_colors=['#28a745', '#dc3545']
                    )
                ]
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12,
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            fig.update_layout(
                title={
                    'text': f"Poll Progress Overview<br><sub>{submitted_count}/{total_count} Responses Collected</sub>",
                    'x': 0.5,
                    'font': {'size': 16, 'family': 'Inter'}
                },
                showlegend=True,
                height=400,
                margin=dict(t=80, b=40, l=40, r=40),
                font=dict(family="Inter", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            # Add center text
            fig.add_annotation(
                text=f"<b>{completion_rate:.1f}%</b><br>Complete",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Detailed user list with enhanced styling
            st.subheader("👤 Detailed User Status")
            if stats:
                # Filter options
                col1, col2 = st.columns([1, 3])
                with col1:
                    show_filter = st.selectbox(
                        "🔍 Filter by Status:", ["All", "Submitted", "Pending"],
                        help="Filter users by their submission status"
                    )
                # Create DataFrame for better display
                df_data = []
                for emp_id, emp_name, status in stats:
                    df_data.append(
                        {
                            'Employee ID': emp_id,
                            'Employee Name': emp_name,
                            'Status': '✅ Submitted' if status == 1 else '❌ Pending',
                            'Status_Raw': status
                        }
                    )
                df = pd.DataFrame(df_data)
                if show_filter == "Submitted":
                    df_filtered = df[df['Status_Raw'] == 1]
                elif show_filter == "Pending":
                    df_filtered = df[df['Status_Raw'] == 0]
                else:
                    df_filtered = df

                # Display filtered data
                display_df = df_filtered[[
                    'Employee ID', 'Employee Name', 'Status']].copy()
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Employee ID": st.column_config.NumberColumn(
                            "Employee ID",
                            help="Employee identification number",
                            format="%d"
                        ),
                        "Employee Name": st.column_config.TextColumn(
                            "Employee Name",
                            help="Full name of the employee"
                        ),
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Current submission status"
                        )
                    }
                )
    elif password != "":
        st.error("❌ Invalid password")
        st.stop()
    else:
        st.info("🔐 Please enter the admin password to continue")
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Regular user interface (only shown when not in admin mode)

if admin_mode == "User":
    ist_today = get_ist_date()
    hours, minutes, seconds, total_seconds, ended = get_timer_info()

    header_html = f"""
    <div class="main-header">
        <div class="header-top">
            <h1 class="main-title">🍽️ Dinner Polling System</h1>
        </div>
        <div class="header-bottom">
            <div class="date-info">Today's Date (IST): {ist_today}</div>
            <div class="timer-container">
                <div class="timer-box" id="timerDisplay">
                    {'Poll ends in ' + f"{hours:02d}:{minutes:02d}:{seconds:02d}" if not ended else 'Poll Ended'}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    if not ended:
        timer_js = f"""
        <script>
            let totalSeconds = {total_seconds};
            function updateTimer() {{
                if (totalSeconds <= 0) {{
                    const t = parent.document.getElementById('timerDisplay');
                    if (t) {{ t.innerHTML = 'Poll Ended'; }}
                    return;
                }}
                const h = Math.floor(totalSeconds / 3600);
                const m = Math.floor((totalSeconds % 3600) / 60);
                const s = totalSeconds % 60;
                const t = parent.document.getElementById('timerDisplay');
                if (t) {{
                    t.innerHTML = 'Poll ends in ' + String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}
                totalSeconds--;
            }}
            updateTimer();
            setInterval(updateTimer, 1000);
        </script>
        """
        components.html(timer_js, height=0)

    if not is_poll_time_active() or is_poll_manually_ended():
        st.error(
            f"⏰ Poll is not active. It ended at {get_poll_end_time()} IST.")
        st.stop()

    users = get_users()
    today = str(ist_today)
    submitted_users = [f"{emp_id}: {emp_name}" for uid, emp_id,
                       emp_name in users if get_user_submission_status(uid, today)]
    not_submitted_users = [f"{emp_id}: {emp_name}" for uid, emp_id,
                           emp_name in users if not get_user_submission_status(uid, today)]

    # Status section
    st.markdown(f"""
    <div class="section">
        <h3>📊 Current Poll Status</h3>
        <div class="status-grid">
            <div class="status-card success">
                <div class="status-number">{len(submitted_users)}</div>
                <div class="status-label">✅ Submitted</div>
            </div>
            <div class="status-card danger">
                <div class="status-number">{len(not_submitted_users)}</div>
                <div class="status-label">❌ Pending</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User lists
    col1, col2 = st.columns(2)
    with col1:
        if submitted_users:
            with st.expander(f"👥 View {len(submitted_users)} Submitted Users"):
                for user in submitted_users:
                    st.markdown(
                        f"<div class='user-list-item'>• {user}</div>", unsafe_allow_html=True)
    with col2:
        if not_submitted_users:
            with st.expander(f"👥 View {len(not_submitted_users)} Pending Users"):
                for user in not_submitted_users:
                    st.markdown(
                        f"<div class='user-list-item'>• {user}</div>", unsafe_allow_html=True)

    # Enhanced Progress bar with real-time updates
    total_users = len(users)
    submitted_count = len(submitted_users)
    pending_count = len(not_submitted_users)
    progress_percent = (submitted_count / total_users) * \
        100 if total_users else 0

    # Combined progress and poll form section with seamless design
    current_time = datetime.now().strftime('%H:%M:%S')
    st.markdown(f"""
    <div class="combined-poll-section">
        <div class="progress-section-integrated">
            <div class="progress-header">
                <h4>📊 Poll Progress</h4>
                <div class="progress-stats">
                    <span class="stat-item submitted">✅ {submitted_count} Submitted</span>
                    <span class="stat-item pending">❌ {pending_count} Pending</span>
                    <span class="stat-item total">👥 {total_users} Total</span>
                </div>
            </div>
            <div class="progress-container" data-progress="{progress_percent:.1f}">
                {f'<div class="progress-bar progress-animated" style="width: {progress_percent}%;" data-width="{progress_percent}"><span class="progress-text">{progress_percent:.1f}%</span></div>' if progress_percent > 0 else '<div class="progress-empty"><span class="progress-text-empty">0.0% - No submissions yet</span></div>'}
            </div>
            <div class="progress-footer">
                <small>Progress updates automatically with each submission • Last updated: {current_time}</small>
            </div>
        </div>
        <div class="poll-form-integrated">
            <h3 class="poll-form-title">📝 Submit Your Response</h3>
    """, unsafe_allow_html=True)

    # Poll form content without the separate container
    # Title is now handled in the HTML above

    # Create tabs for submit and reset
    tab1, tab2 = st.tabs(["🚀 Submit Poll", "🔄 Reset My Submission"])

    with tab1:
        employee_id_input = st.text_input(
            "🆔 Employee ID:", placeholder="Enter your Employee ID (e.g., 1001)", key="submit_emp_id")
        if st.button("🚀 Submit Poll", use_container_width=True, key="submit_poll_btn"):
            if not employee_id_input.strip():
                st.warning("⚠️ Please enter your Employee ID.")
            else:
                try:
                    employee_id = int(employee_id_input)
                except ValueError:
                    st.error("❌ Employee ID must be a number.")
                else:
                    found_user = next(
                        ((uid, name) for uid, emp_id, name in users if emp_id == employee_id), None)
                    if found_user:
                        uid, name = found_user
                        if get_user_submission_status(uid, today):
                            st.info(f"ℹ️ {name} has already submitted today.")
                            st.info(
                                "📝 You can reset your submission using the 'Reset My Submission' tab if needed.")
                        else:
                            submit_poll(uid, today)
                            st.success(
                                f"🎉 Thanks {name}, your response has been recorded.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Employee ID not found.")

    with tab2:
        st.markdown("📝 **Reset Your Submission**")
        st.info(
            "ℹ️ Use this if you want to change your submission or if you submitted by mistake.")

        reset_employee_id_input = st.text_input(
            "🆔 Employee ID:", placeholder="Enter your Employee ID (e.g., 1001)", key="reset_emp_id")

        if st.button("🔄 Reset My Submission", use_container_width=True, key="reset_my_submission", type="secondary"):
            if not reset_employee_id_input.strip():
                st.warning("⚠️ Please enter your Employee ID.")
            else:
                try:
                    reset_employee_id = int(reset_employee_id_input)
                except ValueError:
                    st.error("❌ Employee ID must be a number.")
                else:
                    # Simple direct reset like admin - no complex confirmations
                    user_info = get_user_by_emp_id(reset_employee_id)
                    if user_info:
                        if reset_user_submission(user_info['id'], today):
                            st.success(f"✅ Reset submission for {user_info['emp_name']} (ID: {reset_employee_id})")
                            st.info("📝 You can now submit again using the 'Submit Poll' tab.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning(f"No submission found for {user_info['emp_name']} today or reset failed")
                    else:
                        st.error("❌ Employee ID not found")

    # Close the combined poll section
    st.markdown('</div></div>', unsafe_allow_html=True)

    with st.expander("ℹ️ Need Help?"):
        st.markdown("""
        **How to use this system:**
        
        **🚀 To Submit:**
        1. Go to the "Submit Poll" tab
        2. Enter your Employee ID
        3. Click **Submit Poll**
        4. Get confirmation 🎉
        
        **🔄 To Reset Your Submission:**
        1. Go to the "Reset My Submission" tab
        2. Enter your Employee ID
        3. Click **Reset My Submission**
        4. Confirm the reset
        5. You can now submit again

        **📝 Notes:**
        - One submission per day (unless reset)
        - Submit before poll end time
        - You can reset your submission if needed
        - Resetting allows you to submit again
        
        **❓ Common Questions:**
        - **Can I change my submission?** Yes, use the reset feature
        - **What if I submitted by mistake?** Use the reset feature
        - **Can I submit multiple times?** Only after resetting
        """)

        # Add a quick status check
        st.markdown("---")
        st.markdown("**🔍 Quick Status Check:**")
        quick_check_id = st.text_input(
            "Enter your Employee ID to check status:", key="quick_status_check")
        if quick_check_id:
            try:
                check_emp_id = int(quick_check_id)
                found_user = next(
                    ((uid, name) for uid, emp_id, name in users if emp_id == check_emp_id), None)
                if found_user:
                    uid, name = found_user
                    status = get_user_submission_status(uid, today)
                    if status:
                        st.success(f"✅ {name}, you have submitted today")
                    else:
                        st.info(f"📝 {name}, you haven't submitted today yet")
                else:
                    st.error("❌ Employee ID not found")
            except ValueError:
                st.error("❌ Please enter a valid Employee ID")
