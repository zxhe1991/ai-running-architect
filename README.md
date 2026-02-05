# AI Running Architect 🏃

A comprehensive Streamlit application that provides personalized running coaching advice by analyzing historical running data, current run performance, and user profile.

## Features

- **Historical Data Analysis**: Upload and index your Garmin running CSV data for semantic search
- **Current Run Analysis**: Upload csv file to analyze today's run with advanced metrics:
  - Cardiac Drift (efficiency drop analysis)
  - Pacing Variance (run type classification)
  - Cadence, Vertical Oscillation, Stride Length metrics
- **AI-Powered Coaching**: Get personalized training plans and advice based on:
  - Your current performance vs. goals
  - Historical similar runs
  - Subjective feelings
  - Available training time

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API key:
```
SUPER_MIND_API_KEY=your_api_key_here
SUPER_MIND_BASE_URL=https://space.ai-builders.com/backend/v1
```

3. Run the application:
```bash
streamlit run app.py
```

## Deployment

This application can be deployed to `ai-builders.space` platform. See `deploy-config.json` for deployment configuration.

## Requirements

- Python 3.11+
- Streamlit
- OpenAI API access (via AI Builder Space)
- Garmin historical running data (CSV format)
- Garmin latest running data (CSV format)
