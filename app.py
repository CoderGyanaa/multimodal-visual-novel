"""
app.py
The Multi-Modal Visual Novel — Capstone Mini-Project
MirAI School of Technology | Virtual Summer Internship 2026 | AI Builder Track

Combines: stateful Gemini text generation, structured JSON output,
dynamic UI generation, Pollinations.ai image generation, gTTS narration,
and graceful failure handling.
"""

import streamlit as st

from utils import (
    GENRES,
    ART_STYLES,
    get_gemini_client,
    generate_scene,
    fetch_scene_image,
    synthesize_narration,
    StoryError,
    ImageError,
    AudioError,
)

# ----------------------------------------------------------------
# Page Config + Styling
# ----------------------------------------------------------------
st.set_page_config(page_title="The Multi-Modal Visual Novel", page_icon="📖", layout="centered")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------
# Phase 1: The Director's Cut — cached Gemini client + session state
# ----------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_cached_client(api_key: str):
    return get_gemini_client(api_key)


if "chat_contents" not in st.session_state:
    st.session_state.chat_contents = []      # Gemini conversation history
if "story_log" not in st.session_state:
    st.session_state.story_log = []          # Rendered scenes: text, image, audio, options
if "story_started" not in st.session_state:
    st.session_state.story_started = False

with st.sidebar:
    st.markdown("### 📖 Story Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key here",
        help="Get a free key at aistudio.google.com/apikey",
    )
    st.caption("🔑 Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)")

    genre = st.selectbox("Story Genre", GENRES)
    art_style = st.selectbox("Art Style", list(ART_STYLES.keys()))

    st.markdown("---")
    if st.button("🔄 Restart Story"):
        st.session_state.chat_contents = []
        st.session_state.story_log = []
        st.session_state.story_started = False
        st.rerun()

st.markdown("<div class='novel-title'>📖 The Multi-Modal Visual Novel</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='novel-subtitle'>An AI-narrated, AI-illustrated, AI-narrated-out-loud "
    "choose-your-own-adventure.</div>",
    unsafe_allow_html=True,
)


def advance_story(action_text: str):
    """
    Runs one full turn of the engine:
    Phase 2 (structured JSON scene) -> Phase 4 (image + audio) -> log the scene.
    Every external call is wrapped per Phase 5 so a single failure never
    crashes the app.
    """
    if not api_key:
        st.error("Please add your Gemini API key in the sidebar.")
        return

    client = get_cached_client(api_key)

    st.session_state.chat_contents.append(
        {"role": "user", "parts": [{"text": action_text}]}
    )

    # ---------------- Phase 2: Structured JSON Engine ----------------
    with st.spinner("The narrator is thinking..."):
        try:
            scene = generate_scene(client, genre, st.session_state.chat_contents)
        except StoryError as e:
            st.error(f"Story engine error: {e}")
            st.session_state.chat_contents.pop()  # undo the failed turn
            return

    st.session_state.chat_contents.append(
        {"role": "model", "parts": [{"text": scene["story_text"]}]}
    )

    # ---------------- Phase 4: Multi-Media Rendering ----------------
    image_bytes = None
    with st.spinner("Painting the scene..."):
        try:
            image_bytes = fetch_scene_image(scene["image_prompt"], art_style)
        except ImageError:
            st.toast("Image server is busy, skipping visual...")

    audio_bytes = None
    with st.spinner("Recording narration..."):
        try:
            audio_bytes = synthesize_narration(scene["story_text"])
        except AudioError:
            st.toast("Narration engine is busy, skipping audio...")

    st.session_state.story_log.append(
        {
            "story_text": scene["story_text"],
            "image": image_bytes,
            "audio": audio_bytes,
            "options": scene.get("options", []),
        }
    )
    st.session_state.story_started = True


# ----------------------------------------------------------------
# Entry point: start the story
# ----------------------------------------------------------------
if not st.session_state.story_started:
    st.write("Choose your genre and art style in the sidebar, then begin.")
    if st.button("▶️ Begin Story"):
        advance_story(f"Begin a new {genre} story.")
        st.rerun()

# ----------------------------------------------------------------
# Phase 4 (cont.): Render the full story log so nothing disappears
# ----------------------------------------------------------------
for i, scene in enumerate(st.session_state.story_log):
    st.markdown("<div class='scene-card'>", unsafe_allow_html=True)

    if scene["image"]:
        st.image(scene["image"], use_container_width=True)

    st.markdown(f"<div class='scene-text'>{scene['story_text']}</div>", unsafe_allow_html=True)

    if scene["audio"]:
        st.audio(scene["audio"], format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Phase 3: Dynamic UI Generation — buttons built from the AI's own options
# ----------------------------------------------------------------
if st.session_state.story_log:
    latest_options = st.session_state.story_log[-1]["options"]
    st.markdown("#### What do you do?")
    for idx, option in enumerate(latest_options):
        if st.button(option, key=f"option_{len(st.session_state.story_log)}_{idx}"):
            advance_story(option)
            st.rerun()
