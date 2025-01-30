
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import subprocess
import tempfile
import json
import os
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# initialize the flask application
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///logs.db" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# defining the loging model
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500))
    response = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

# Load the Knowledge Base (from JSON file)
def load_knowledge_base():
    kb = []
    kb_dir = "./knowledge_base"
    if not os.path.exists(kb_dir):
        os.makedirs(kb_dir)
    
    for file in os.listdir(kb_dir):
        path = os.path.join(kb_dir, file)
        if file.endswith(".json"):
            with open(path, "r") as f:
                kb.extend(json.load(f))  #here json will contain the list of q&a.
    return kb

# read the file from storedata.txt
def load_context():
    try:
        with open('storedata.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Context file not found."

# sentence transformer model for vectorizing the text
embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 

# Vectorize the knowledge base
def vectorize_kb(kb):
    """Converts knowledge base text into vector embeddings."""
    texts = [item["question"] for item in kb]
    vectors = embedding_model.encode(texts, convert_to_numpy=True)
    return vectors

# Create FAISS index for fast retrieval
def create_faiss_index(vectors):
    """Create a FAISS index from knowledge base vectors."""
    index = faiss.IndexFlatL2(vectors.shape[1])  # L2 distance for similarity search
    index.add(vectors)  # Add vectors to the index
    return index

# Vectorize and index the knowledge base
kb = load_knowledge_base()
kb_vectors = vectorize_kb(kb)
faiss_index = create_faiss_index(kb_vectors)

# Match query with Knowledge Base using vector search
def generate_response(query):
    """Generates response based on vector search or uses Falcon model if no match found."""
    
    # Vectorize the query
    query_vector = embedding_model.encode([query], convert_to_numpy=True)

    # Perform the search in FAISS index
    k = 1  # Number of closest results to return
    distances, indices = faiss_index.search(query_vector, k)

    # If a match is found (distance is low), return the corresponding answer
    if distances[0][0] < 0.7:  # Adjust threshold if needed
        best_match = kb[indices[0][0]]
        return best_match["answer"]  # Return the corresponding answer
    
    # If no match is found or distance is too high, use Falcon model for further assistance
    context = load_context()  # Load context from storedata.txt
    prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"

    try:
        # Use a temporary file to store the prompt
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
            temp_file.write(prompt)
            temp_file_path = temp_file.name

        # Use subprocess to call Ollama CLI with the temporary file
        result = subprocess.run(
            ['ollama', 'run', 'falcon', '--file', temp_file_path],
            capture_output=True, text=True, check=True
        )

        response = result.stdout.strip()

        # Clean up the temporary file
        os.remove(temp_file_path)

    except subprocess.CalledProcessError as e:
        response = "I'm sorry, I couldn't process your request."
    
    return response

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response = generate_response(query)

    # Log interaction in SQLite
    log = Log(query=query, response=response, timestamp=datetime.now(timezone.utc))
    db.session.add(log)
    db.session.commit()

    return jsonify({"response": response})

@app.route("/admin/update_kb", methods=["POST"])
def update_kb():
    # Reload knowledge base from JSON files and re-index
    global kb, faiss_index, kb_vectors
    kb = load_knowledge_base()
    kb_vectors = vectorize_kb(kb)
    faiss_index = create_faiss_index(kb_vectors)
    return jsonify({"message": "Knowledge base updated and re-indexed successfully!"})

@app.route("/admin/view_logs", methods=["GET"])
def view_logs():
    logs = db.session.query(Log).all()  # Correct way to query all logs
    logs_data = [
        {
            "query": log.query,
            "response": log.response,
            "timestamp": log.timestamp.isoformat()  # Convert datetime to string
        }
        for log in logs
    ]
    return jsonify(logs_data)

if __name__ == "__main__":
    app.run(debug=True)


