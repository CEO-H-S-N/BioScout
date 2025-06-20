# 🌿 BioScout Islamabad

**BioScout Islamabad** is an AI-powered platform that allows communities in Islamabad to record, identify, and explore local biodiversity using species image recognition and Retrieval-Augmented Generation (RAG) Q&A.

---

## 📌 Overview

This project was developed for the **AI for a Sustainable Future Hackathon** to tackle urban biodiversity loss. It focuses on:

- Community-submitted species observations
- AI-assisted species image identification
- A smart Q&A system using RAG
- Islamabad’s Margalla Hills and surrounding regions

---

## 🚀 Features

- 📸 Upload photos to get AI-predicted species
- 🗺️ Submit species sightings with location
- ❓ Ask biodiversity questions (e.g. "Are there leopards near Rawal Lake?")
- 🔍 Intelligent retrieval of species facts
- 🏆 Mock gamification (Top Observer badge)

---

## 🛠 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Tools**:
  - Hugging Face Image Models (simulated)
  - RAG using sentence-transformers (mocked)
- **Database**: CSV-based storage

---

🌿 Example Queries

What birds are common in Margalla Hills?
Are there recent leopard sightings near Rawal Lake?

---

📈 Future Ideas

User accounts and authentication

Community-validated species IDs

Multilingual Q&A (Urdu)

Offline field mode with PWA support

---

📜 License
This project is open-source under the MIT License.

---

---

## ✅ 2. `requirements.txt`

```txt
streamlit
pandas
numpy
Pillow
sentence-transformers
scikit-learn
```

## 💾 Installation

```bash
git clone https://github.com/yourusername/bioscout-islamabad.git
cd bioscout-islamabad

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```
---

📁 File Structure

```txt
graphql
Copy
Edit
BioScout/
│
├── app.py                   # Main Streamlit app
├── utils/                   # API and RAG helpers
├── rag_knowledge/           # Biodiversity knowledge base (text snippets)
├── observations.csv         # Simulated observations
├── scores.csv               # Leaderboard mockup
├── requirements.txt         # Dependencies
└── README.md                # Project description
