# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.pii import mask_pii
from backend.rag import RAGIndex, load_seed_docs
from backend.db import init_db, create_user, get_purchases_for_user, add_purchase
from backend.utils import nearest_stores
import json
import os
from dotenv import load_dotenv
import requests
from typing import Optional

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
init_db()  # Initialize DB tables

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL_NAME = os.environ.get("GROQ_MODEL_NAME") or "your_groq_model_name_here"

app = FastAPI(title="H-002 Hyper-Personalized Customer Agent")

# ----------------------------
# RAG index
# ----------------------------
BASE_DIR = os.path.dirname(__file__)
rag = RAGIndex(
    index_path=os.path.join(BASE_DIR, "faiss_index.index"),
    meta_path=os.path.join(BASE_DIR, "meta.json"),
)
if not rag.load():
    # Build from seed docs if index not found
    docs = load_seed_docs(os.path.join(BASE_DIR, "..", "data", "seed_docs"))
    rag.build_from_docs(docs)


# ----------------------------
# Request model
# ----------------------------
class ChatRequest(BaseModel):
    message: str
    location: Optional[dict] = None
    user_id: Optional[str] = None
    new_user: Optional[bool] = False  # True if onboarding a new user
    track_purchase: Optional[dict] = None  # {"store_name": str, "category": str, "amount": float}


# ----------------------------
# Helper functions
# ----------------------------
def build_rag_context(user_message: str, user_id: str = None, location: dict = None) -> str:
    """
    Build the context for LLM including:
    - RAG seed docs
    - Nearest stores + promos
    - Past user purchases
    """
    context_parts = []

    # 1️⃣ Seed docs from RAG
    retrieved = rag.retrieve(user_message, k=3)
    if retrieved:
        retrieved_text = "\n".join([r["text"] for r in retrieved])
        context_parts.append("Seed docs:\n" + retrieved_text)

    # 2️⃣ Nearest stores
    stores_file = os.path.join(BASE_DIR, "..", "data", "stores.json")
    stores_list = []
    try:
        with open(stores_file, "r", encoding="utf-8") as f:
            stores_list = json.load(f)
    except FileNotFoundError:
        pass

    if location and stores_list:
        nearest = nearest_stores(location.get("lat"), location.get("lng"), stores_list, max_results=3)
        store_text = "Nearby stores:\n"
        for s in nearest:
            store_text += f"- {s['name']} ({s['distance_m']}m away) | Promos: "
            store_text += ", ".join([p["desc"] for p in s.get("promos", [])]) + "\n"
        context_parts.append(store_text)

    # 3️⃣ Past purchases
    if user_id:
        purchases = get_purchases_for_user(user_id, limit=5)
        if purchases:
            purchase_text = "Past purchases:\n"
            for p in purchases:
                purchase_text += f"- {p.store_name} at {p.timestamp.strftime('%Y-%m-%d')} | {p.category}\n"
            context_parts.append(purchase_text)

    return "\n".join(context_parts)


def generate_with_groq(prompt: str) -> str:
    """
    Send the prompt to Groq API and get generated response.
    """
    if not GROQ_API_KEY or not GROQ_MODEL_NAME:
        raise RuntimeError("GROQ_API_KEY and GROQ_MODEL_NAME must be set")

    url = f"https://api.groq.ai/v1/models/{GROQ_MODEL_NAME}/generate"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "prompt": prompt,
        "max_output_tokens": 256,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Groq API Error: {response.text}")
    data = response.json()
    # Extract generated text; depending on Groq API, may need to adjust
    return data.get("output_text", data.get("text", ""))


# ----------------------------
# Chat endpoint
# ----------------------------
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message:
        raise HTTPException(400, "Message required")

    # 1️⃣ Mask PII in user message
    masked_message = mask_pii(req.message)

    # 2️⃣ Handle new / returning users
    if req.new_user or not req.user_id:
        user_id = f"user_{os.urandom(4).hex()}"
        user = create_user(user_id=user_id)
    else:
        user_id = req.user_id
        user = create_user(user_id=user_id)  # also acts like "get or create"

    # 3️⃣ Track purchase if user clicked "I'm going"
    if req.track_purchase:
        add_purchase(
            user_id=user_id,
            store_name=req.track_purchase.get("store_name"),
            category=req.track_purchase.get("category"),
            amount=req.track_purchase.get("amount", 0.0)
        )

    # 4️⃣ Load stores for dynamic recommendations
    stores_file = os.path.join(BASE_DIR, "..", "data", "stores.json")
    stores_list = []
    try:
        with open(stores_file, "r", encoding="utf-8") as f:
            stores_list = json.load(f)
    except FileNotFoundError:
        pass

    nearest = []
    if req.location and stores_list:
        nearest = nearest_stores(
            req.location.get("lat"),
            req.location.get("lng"),
            stores_list,
            max_results=3
        )

    # 5️⃣ Build dynamic RAG context
    context = build_rag_context(masked_message, user_id=user_id, location=req.location)

    # 6️⃣ Compose final prompt
    prompt = f"""
You are a helpful retail assistant. Only use the context provided.
User message: {masked_message}
Context: {context}
Answer concisely, friendly, and suggest the best store based on user history and location.
"""

    # 7️⃣ Generate reply from Groq
    try:
        reply = generate_with_groq(prompt)
    except Exception as e:
        reply = f"Error generating response: {e}"

    # 8️⃣ API response
    return {
        "reply": reply,
        "context_used": context,
        "user_id": user_id,
        "store_recommendations": nearest  # 🔥 added to enable button actions
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
