# groundtruthhackathon
# Hyper-Personalized Customer Experience Automation — H‑002

**Tagline:** A context-aware retail assistant that delivers real-time hyper‑personalized recommendations using location, history, and AI — deployed as a fully open‑source system.

---

## 1. The Problem (Real‑World Scenario)

Modern retail customers expect instant, smart support. But most chatbots today give generic answers:

> “Is the store open?” → *Please visit our website.*
> “Do you have size 10?” → *We will get back to you.*

In reality, customers expect a bot to *know* them — their preferences, past purchases, and context.

### Real Pain Point

Brands lose customers because their support systems are rigid and impersonal. When a customer is outside a store and says:

> “I’m cold.”

A typical bot responds: **“How may I assist you?”** — and loses the opportunity.

---

## 2. The Solution — H‑002

H‑002 is a **Hyper‑Personalized Customer Support Agent** that adapts instantly to each user.

### Example Interaction

User: *“I’m cold.”*

System determines:

* User is physically near *Starbucks*
* User previously purchased *hot drinks*
* Active promo: *10% off Hot Cocoa*

Bot replies:

> “There’s a Starbucks 50m away. Hot Cocoa is available — and you have a 10% coupon. Should I book your order?”

### Expected End Result

For the User:

```
Input: Send a text to the chatbot
Action: System automatically uses the user's context + past behavior
Output: A personal, specific, actionable recommendation
```

---

## 3. Technical Approach

H‑002 is engineered as a **production‑ready** multi‑service pipeline — not a simple chatbot script.

### System Architecture

| Component                     | Responsibility                             |
| ----------------------------- | ------------------------------------------ |
| Streamlit Frontend            | Onboarding, geolocation, chat UI           |
| FastAPI Backend               | Core inference + user tracking             |
| SQLite (SQLModel)             | Secure user profile + purchase history     |
| FAISS + Sentence‑Transformers | Personalized retrieval (RAG)               |
| Local LLM (optional)          | Response generation — no PII leaves system |

### Privacy Guarantee

No raw customer data is sent to third‑party LLMs.
All sensitive PII is masked by the backend before inference.

---

## 4. Tech Stack

| Layer            | Technology                      |
| ---------------- | ------------------------------- |
| Language         | Python 3.11                     |
| Frontend         | Streamlit + geolocation capture |
| Backend          | FastAPI + Uvicorn               |
| Database         | SQLite (SQLModel ORM)           |
| Retrieval Engine | FAISS + Sentence‑Transformers   |
| Vector Model     | `all-MiniLM-L6-v2`              |
| Infrastructure   | Docker + Docker Compose         |

---

## 5. Challenges & Learnings

### Challenge 1 — Maintaining Privacy

The AI cannot be allowed to see raw PII.

> Solution → PII Masking Layer
> Before any prompt is processed, phone numbers, emails, and names are masked and re‑mapped afterward.

### Challenge 2 — Real‑Time Personalization

Static chatbots cannot react to geography.

> Solution → Location‑Aware Context Engine
> The system calculates distance to nearby stores and maps promotions to the closest relevant location.

---

## 6. Visual Proof (Expected Demo Screens)

* User onboarding (New / Returning customer)
* “Use current location” popup
* Personalized store recommendations with distance
* Purchase history timeline
* RAG‑powered smart chat

---

## 7. How to Run

```bash
# 1. Clone Repository
git clone https://github.com/username/H-002.git
cd H-002

# 2. Add Environment Variables
cp assets/example_env.template .env

# 3. Run via Docker
docker-compose up --build

# 4. Open Frontend
localhost:8501  # Streamlit

# 5. Backend API Docs
localhost:8000/docs
