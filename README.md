# FAQ Assistant

FAQ Assistant is a Flask-based application that allows users to ask questions and receive answers based on a predefined knowledge base. It utilizes vector embeddings and FAISS for fast semantic search and retrieval.

## Features
- 🏷️ **Preloaded FAQ Database:** Loads initial FAQs from `faqs.json`.
- 🔄 **Dynamic Knowledge Base Updates:** `large_faqs.json` is used to update the knowledge base.
- 🚀 **Vector Search with FAISS:** Uses FAISS for efficient question matching.
- 💬 **Interactive Chat Interface:** Users can ask questions through a web UI.
- 📊 **Admin Panel for Logs & KB Management:** View query logs and update the knowledge base dynamically.
- 🛠️ **Embeddings with Sentence Transformers:** Uses `all-MiniLM-L6-v2` for text embeddings.
- 🔍 **Fallback to Falcon Model:** If no match is found, it generates an answer using the Falcon model.
- 📂 **Database Logging:** Stores queries and responses using SQLite (`logs.db`).

## Tech Stack
- **Backend:** Flask, FAISS, SQLAlchemy, Sentence Transformers
- **Frontend:** HTML, Bootstrap, TailwindCSS
- **Database:** SQLite (`logs.db`)
- **ML Models:** `all-MiniLM-L6-v2` for embeddings, Falcon model for fallback responses

## Installation

### Prerequisites
Ensure you have Python 3.8+ installed.

### Clone the Repository
```sh
git clone https://github.com/your-repo/faq-assistant.git
cd faq-assistant
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Run the Application
```sh
python app.py
```

The app will start at `http://127.0.0.1:5000/`

## API Endpoints

### 1. Ask a Question
**Endpoint:** `/ask`
**Method:** `POST`
**Payload:** `{ "query": "Your question here" }`
**Response:** `{ "response": "The answer from the knowledge base or Falcon model." }`

### 2. Update Knowledge Base
**Endpoint:** `/admin/update_kb`
**Method:** `POST`
**Response:** `{ "message": "Knowledge base updated and re-indexed successfully!" }`

### 3. View Logs
**Endpoint:** `/admin/view_logs`
**Method:** `GET`
**Response:** `[{ "query": "User query", "response": "Bot response", "timestamp": "YYYY-MM-DDTHH:MM:SS" }]`

## Project Structure
```
proj/
┣ instance/
┃ ┗ logs.db
┣ knowledge_base/
┃ ┣ faqs.json              # Initial FAQ data
┃ ┣ large_faqs.json        # Updated FAQ data
┃ ┣ main.py                # Script to process FAQs into structured text
┃ ┗ storedata.txt          # Context file for fallback responses
┣ logs/                    # Directory for logs
┣ static/                  # Static assets
┣ templates/
┃ ┣ admin.html             # Admin panel
┃ ┗ index.html             # User chat interface
┣ app.py                   # Flask application
┗ requirements.txt         # Dependencies
```

## Admin Panel
Access the admin panel at `http://127.0.0.1:5000/admin`

### Admin Functions
- **View Query Logs:** Displays user queries and responses.
- **Update Knowledge Base:** Reloads and indexes new FAQ data from `large_faqs.json`.

