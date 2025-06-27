import streamlit as st
import openai
import json
from datetime import datetime

# === OpenRouter Configuration ===
client = openai.OpenAI(
    api_key=st.secrets["OPENROUTER_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
MEMORY_FILE = "memory_db.json"

EMOTION_COLORS = {
    "joy": "#FFD700", "joy_light": "#FFF9C4",
    "sadness": "#4169E1", "sadness_light": "#B0C4DE",
    "anger": "#DC143C", "anger_light": "#FFCCCB",
    "curiosity": "#7FFFD4", "curiosity_light": "#E0FFFF",
    "awe": "#8A2BE2", "confusion": "#FF8C00",
    "peace": "#98FB98", "loneliness": "#708090"
}

def get_emotional_response(prompt):
    system_msg = (
        "You are an emotionally-aware AI. First, reply to the user. Then label the emotion "
        "from: joy, joy_light, sadness, sadness_light, anger, anger_light, curiosity, curiosity_light, "
        "awe, confusion, peace, loneliness. Format:\n\n[reply]\n\n[emotion]"
    )
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You're a kind emotional AI"},
                {"role": "user", "content": "I'm feeling excited about this project!"}
            ]
       )
        content = response.choices[0].message.content.strip()
        if "\n\n" in content:
            reply, emotion = content.split("\n\n")[:2]
            emotion = emotion.lower().strip()
        else:
            reply, emotion = content, "curiosity"
        color = EMOTION_COLORS.get(emotion, "#D3D3D3")
        return reply, emotion, color
    except Exception as e:
        return f"Error: {str(e)}", "confusion", "#FF8C00"

def log_emotion(text, emotion, color):
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append({
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "emotion": emotion,
        "color": color
    })
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_soulfile_colors():
    try:
        with open(MEMORY_FILE, "r") as f:
            return [d["color"] for d in json.load(f)]
    except:
        return []

st.set_page_config(page_title="Soulfile v0.3", layout="centered")
if 'soulfile_name' not in st.session_state:
    st.session_state.soulfile_name = "Soulfile"

with st.sidebar:
    st.session_state.soulfile_name = st.text_input("Name your AI companion:", value=st.session_state.soulfile_name, max_chars=20)

st.title(f"🧬 {st.session_state.soulfile_name}: Emotional Memory Prototype")
st.markdown("_This AI remembers how you feel over time._")
user_input = st.text_input("Speak to your Soulfile:", value=st.session_state.get("user_input", ""))

if user_input:
    reply, emotion, color = get_emotional_response(user_input)
    log_emotion(user_input, emotion, color)
    st.markdown(f"**{st.session_state.soulfile_name} says:** {reply}")
    st.markdown(f"_Emotional tone:_ **{emotion}** `{color}`")
    st.session_state.user_input = ""

colors = get_soulfile_colors()
if colors:
    st.subheader("🧠 Your Emotional Timeline")
    st.markdown("<div style='display:flex; flex-wrap:wrap;'>" + "".join([
        f"<div title='{i+1}' style='width:20px; height:20px; background-color:{c}; margin:2px; border-radius:3px;'></div>"
        for i, c in enumerate(colors[-100:])
    ]) + "</div>", unsafe_allow_html=True)
else:
    st.info("No emotional memory yet. Start speaking to grow your trace.")
