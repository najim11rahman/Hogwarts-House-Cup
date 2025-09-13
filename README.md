# Hogwarts House Cup Leaderboard

## Overview
This project is a live leaderboard for the **Hogwarts House Cup** with **React frontend** and **Python Flask backend**.  
It tracks and displays points for the four houses (Gryff, Slyth, Raven, Huff) in real time.  

The leaderboard supports different **time windows** and **live updates** via server-sent events (SSE).

---

## Features

### Backend
- Ingests house point events and stores them locally in **SQLite**.  
- Provides an API to get **house totals** for a specific time window:  
  - Last 5 minutes (`5m`)  
  - Last 1 hour (`1h`)  
  - All time (`all`)  
- Supports **real-time updates** using SSE.

### Frontend
- **Leaderboard UI** for the four houses.  
- **Buttons to select time window** (5 minutes, 1 hour, All time).  
- **Start/Stop live updates** button.  
- Progress bars represent each house’s points relative to the maximum points.  
- Responsive design and smooth transitions for bar updates.  

---

## Folder Structure
hogwarts_leaderboard/
├─ backend/ # Flask API + SQLite
│ ├─ app.py
│ └─ requirements.txt
├─ frontend/ # React app
│ ├─ package.json
│ └─ src/
│ └─ App.js
└─ README.md

---

## Requirements
- Python 3.x
- Node.js + npm
---

## How to Run

- Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

In another terminal, same folder, run python data_gen.py to start ingesting

- Frontend
```bash
cd frontend
npm install
npm start


Open http://localhost:3000 in your browser to see the leaderboard.

- Tech Stack used
Frontend: React.js
Backend: Python Flask
Database: SQLite
Communication: Fetch API + Server-Sent Events (SSE)
Styling: Inline CSS, responsive progress bars
