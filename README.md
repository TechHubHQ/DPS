# Dinner Polling System

A simple Streamlit-based dinner polling system with SQLite database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Run the cleanup job (in separate terminal):
```bash
python cleanup_job.py
```

## Features

- User management with SQLite database
- Daily polling with submission tracking
- Automatic cleanup of old submissions (every 2 days)
- Real-time status display
- **Enhanced Timer Features:**
  - Live countdown timer with warning states
  - Browser notifications when poll is about to end
  - Automatic page refresh when poll ends
  - Visual warning indicators (30 min and 5 min remaining)
- **UI Enhancements:**
  - Real-time form validation with visual feedback
  - Smooth scrolling and loading states
  - Keyboard shortcuts (Ctrl+Enter to submit, Escape to clear)
  - Accessibility features with ARIA labels
  - Dark/Light theme toggle
  - Animated progress counters and charts

## Enhanced JavaScript Features

The application now includes comprehensive client-side enhancements:

- **PollTimer Class**: Advanced timer with callbacks and notifications
- **UIEnhancements Class**: Form validation, keyboard shortcuts, accessibility
- **ProgressAnimator Class**: Smooth animations for counters and progress bars
- **ThemeManager Class**: Dark/light theme switching with localStorage persistence