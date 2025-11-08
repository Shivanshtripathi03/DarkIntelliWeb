DarkIntelliWeb

AI-powered Dark Web Threat Intelligence Dashboard

A cross-environment cybersecurity project combining AI, Flask, and React — designed to detect, analyze, and visualize potential threats from .onion and clearnet sources.



⚙️ Overview

DarkIntelliWeb is an AI-powered threat intelligence platform built to analyze dark web data and provide actionable insights.
It features:

🧠 AI/NLP-based query system

🌐 URL scanning for .onion and normal sites

🔍 Real-time threat classification

🖥️ Modern React-based dashboard

🧩 Flask backend API with modular AI integration




Project Structure

DarkIntelliWeb/
├── frontend/       # React + Vite (TypeScript)
│   ├── src/        # Components, Pages, Styles
│   └── vite.config.ts
│
└── backend/        # Flask + Python (AI/Threat Engine)
    ├── main.py
    ├── requirements.txt
    ├── src/        # Crawler, AI model logic
    └── models/     # (Ignored - heavy files like BERT models)




Tech Stack

Frontend: React.js, TypeScript, Tailwind CSS, Lucide Icons
Backend: Python, Flask, Flask-CORS
AI: BERT / Zero-shot Classification (planned)
Database: SQLite (for testing)
Deployment Target: Local VM or hybrid environment (Mac + Kali)




Setup & Run
🔹 Backend (on Kali VM)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=main.py
flask run --host 0.0.0.0 --port 5000

Frontend (on Mac)
cd frontend
npm install
npm run dev




Why This Project Matters

DarkIntelliWeb is more than a dashboard — it’s a learning and research tool.
It helps cybersecurity enthusiasts understand:

How to safely handle .onion data

How AI models can classify dark web threats

How full-stack intelligence pipelines are designed

🌍 Built for research, learning, and responsible cybersecurity education.




Author

Shivansh Tripathi
🎓 B.Tech CSE, VIT Chennai
💻 Cybersecurity & AI Researcher
🔗 GitHub: Shivanshtripathi03




License

This project is open-source and free to use for educational and research purposes only.
Unauthorized use for real-world dark web scanning or data mining is discouraged.
