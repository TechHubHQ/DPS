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