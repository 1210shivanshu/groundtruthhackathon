import streamlit as st
from streamlit_geolocation import geolocation
import requests
import os

# Backend URL (FastAPI)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="CoffeeBot — Hyper-Personalized Demo", layout="centered")
st.title("CoffeeBot — Hyper-Personalized Customer Assistant")

st.markdown(
    "This demo uses **Groq LLM + Dynamic RAG + Location + Purchase History** "
    "to recommend stores and offers in real-time."
)

# --------------------------------------------------------------------
# Session state initialization
# --------------------------------------------------------------------
for key, default in {
    "user_type": None,
    "user_id": None,
    "history": [],
    "last_recommendations": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------------------------------------
# Select user type
# --------------------------------------------------------------------
if st.session_state.user_type is None:
    st.session_state.user_type = st.radio(
        "Are you a new or returning user?",
        ["New User", "Returning User"],
    )

# --------------------------------------------------------------------
# User ID for returning users
# --------------------------------------------------------------------
if st.session_state.user_type == "Returning User":
    st.session_state.user_id = st.text_input("Enter your User ID for personalized suggestions:")

# --------------------------------------------------------------------
# Location capture
# --------------------------------------------------------------------
loc = geolocation()
if loc:
    st.success(f"📍 Location captured: {loc['lat']:.5f}, {loc['lng']:.5f}")

# --------------------------------------------------------------------
# Chat input
# --------------------------------------------------------------------
user_input = st.text_input("Say something to the bot")

def send_message(track_purchase=None):
    """
    Sends payload to backend and updates UI states.
    """
    payload = {
        "message": user_input if track_purchase is None else "Tracking purchase",
        "new_user": True if st.session_state.user_type == "New User" else False,
        "user_id": st.session_state.user_id,
    }

    if loc:
        payload["location"] = {"lat": loc["lat"], "lng": loc["lng"]}

    if track_purchase:
        payload["track_purchase"] = track_purchase

    try:
        resp = requests.post(BACKEND_URL + "/api/chat", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        bot_reply = data.get("reply", "No reply received.")

        # if backend returns a new userId → store it
        st.session_state.user_id = data.get("user_id", st.session_state.user_id)

        # store store recommendations to enable purchase tracking buttons later
        st.session_state.last_recommendations = data.get("store_recommendations", [])

    except Exception as e:
        bot_reply = f"⚠ Backend error: {e}"

    # Save chat history
    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("bot", bot_reply))


# --------------------------------------------------------------------
# Send button
# --------------------------------------------------------------------
if st.button("Send"):
    if not user_input:
        st.warning("Please enter a message")
    else:
        send_message()

# --------------------------------------------------------------------
# Display Chat History
# --------------------------------------------------------------------
for who, text in st.session_state.history:
    if who == "user":
        st.markdown(f"🧑 **You:** {text}")
    else:
        st.markdown(f"🤖 **Bot:** {text}")

# --------------------------------------------------------------------
# Display store purchase buttons if recommendations exist
# --------------------------------------------------------------------
if st.session_state.last_recommendations:
    st.markdown("---")
    st.subheader("👍 Recommended Stores Near You")
    for store in st.session_state.last_recommendations:
        name = store.get("name")
        category = store.get("recommended_item", "Recommended Item")
        amount = store.get("avg_price", 5)

        if st.button(f"I'm going → Track Purchase at {name}"):
            send_message(
                track_purchase={
                    "store_name": name,
                    "category": category,
                    "amount": amount,
                }
            )
            st.success("📝 Purchase recorded!")

# --------------------------------------------------------------------
# Optional context debugging
# --------------------------------------------------------------------
if st.checkbox("🔍 Show context used by backend"):
    try:
        # fetch last response context (only when available)
        resp = requests.post(BACKEND_URL + "/last_context")
        st.code(resp.json().get("context", ""), language="text")
    except:
        st.info("No context available yet.")
