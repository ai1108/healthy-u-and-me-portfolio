# Health U and Me

A LINE chatbot that helps users track and manage everyday health habits, built as a team project for a university course.

This repo is a clean public snapshot of the project's code (no credential history) — sharing it here as a portfolio piece. The team's original repository, with full project history, remains private for ongoing collaboration.

## Features

- **BMI & Vitals Tracking** (`main.py`, `main1.py`, `utils.py`) — Users log height, weight, blood pressure, and blood sugar over time; the bot calculates BMI, summarizes daily calorie intake, and plots recent trends with matplotlib.
- **Health Knowledge Quiz** (`健康知識王.py`) — Multiple-choice questions on diet, exercise, sleep, and nutrition with instant feedback.
- **Recipe Recommendations** (`健康食譜推薦.py`) — Suggests breakfast/lunch/dinner recipes with ingredients and steps via LINE button templates.
- **Diet Tracker** (`飲食追蹤器.py`) — Lets users log meals by category (breakfast/lunch/dinner/other) and stores structured history per user.
- **Nearby Healthy Eating Finder** (`健康外食go.py`) — Uses the user's shared LINE location and the OpenStreetMap Nominatim API to recommend nearby healthy food options.

## Tech stack

Python, Flask, LINE Messaging API (`linebot` v2 and v3 SDKs), livejson (lightweight JSON persistence), matplotlib, NumPy, OpenCV

## Setup

Credentials are read from environment variables, never hardcoded:

```
export LINE_CHANNEL_ACCESS_TOKEN=your_token
export LINE_CHANNEL_SECRET=your_secret
python main.py
```

## Note

This was a team project for **Soochow University**; the code reflects contributions from multiple team members. This public repo is a single-commit snapshot of the project's current, credential-clean code — it does not include the original development history.
