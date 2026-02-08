# ♟️ Chess Bot Like Me

Chess Bot Like Me is a web-based chess application where users can play against an AI-powered bot that mimics my playstyle through an interactive browser interface.  
The project focuses on game logic, backend development, and real-world cloud deployment.

---

## 🌐 Live Demo

👉 **Play the game here:**  
https://chess-bot-like-me.onrender.com/

---

## 🚀 Features

- Play chess against an AI bot mimicing my playstyle in the browser
- Interactive and responsive chessboard UI
- Legal move validation using python-chess
- Backend-driven game logic with Flask
- Real-time move handling
- Cloud deployment with live access

---

## ⚙️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Browser-based chessboard UI

### Backend
- Python
- Flask
- python-chess

### Deployment
- Render (cloud hosting)
- Gunicorn

---

## 🤖 AI Engine Details

- During **local development**, the bot uses **Stockfish** for strong and accurate gameplay.
- In the **cloud-deployed version**, a lightweight fallback engine is used to ensure stability and compatibility with free cloud infrastructure.
- The architecture is designed so that stronger engines can be re-enabled in future upgrades or premium hosting environments.

---

## 📂 Project Structure

chess-bot-like-me/
├── web/
│ ├── app.py
│ ├── bot_core.py
│ ├── templates/
│ └── static/
├── src/
│ └── engine_wrapper.py
├── requirements.txt
├── README.md
└── LICENSE

---

## 🎯 Learning Outcomes

- Full-stack web application development
- Chess game logic using python-chess
- Backend–frontend integration
- Cloud deployment and debugging
- Handling platform-specific limitations in production environments
- Writing scalable and maintainable project architecture

---

## 👤 Author

**Suraj Paul Choudhury**  
Engineering Student | Computer Science  
Interested in Backend Development, Game Logic, and System Design

---

## 📜 License

This is a personal project developed and maintained by the author.

The project is currently shared for learning, demonstration, and portfolio purposes.  
The author plans to continue improving and extending this project in the future, including potential public hosting and platform releases (such as web or mobile platforms).

All rights are reserved by the author unless stated otherwise.
