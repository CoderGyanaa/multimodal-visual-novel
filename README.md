# 📖 The Multi-Modal Visual Novel

An AI-narrated, AI-illustrated, AI-narrated-*out-loud* "Choose Your Own Adventure" engine — built with **Python**, **Streamlit**, the **Gemini API**, **Pollinations.ai**, and **gTTS**.

Capstone Mini-Project for **MirAI School of Technology's Virtual Summer Internship 2026** — *AI Builder Track*.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red?logo=streamlit)
![Gemini API](https://img.shields.io/badge/Text-Gemini%20API-4285F4?logo=googlegemini)
![Pollinations.ai](https://img.shields.io/badge/Image-Pollinations.ai-ef4444)
![gTTS](https://img.shields.io/badge/Audio-gTTS-34d399)

---

## 📖 Overview

Pick a genre and an art style, hit **Begin Story**, and the app generates a scene: a narrated paragraph, an illustration, spoken narration, and 2–3 choices — all produced by AI in a single turn. Click a choice and the story continues, remembering everything that came before.

This orchestrates three separate AI pipelines into one stateful architecture:
1. **Gemini** generates the story as structured JSON (not just plain text)
2. **Pollinations.ai** turns the AI's own image prompt into an illustration
3. **gTTS** converts the narration into playable audio

---

## ✨ How It Works (Architecture)

### Phase 1 — The Director's Cut
- `@st.cache_resource` caches the Gemini client so it isn't rebuilt on every rerun
- `st.session_state` stores the full conversation history and the rendered story log

### Phase 2 — The Structured JSON Engine
- The system prompt instructs Gemini to respond **only** with a JSON object containing:
  - `story_text` — the narrative paragraph
  - `image_prompt` — a detailed prompt engineered for the image API
  - `options` — a list of 2–3 possible next actions
- `response_mime_type="application/json"` is set on the Gemini request for reliable structured output, and `json.loads()` parses the response into a Python dict

### Phase 3 — Dynamic UI Generation
- Because the AI decides the choices, there's no fixed set of buttons
- A `for` loop iterates over the latest scene's `options` list and generates an `st.button()` for each one, on the fly
- Clicking a button sends that exact choice back to Gemini as the next move

### Phase 4 — Multi-Media Rendering & TTS
- The `image_prompt` is sent to Pollinations.ai and rendered with `st.image()`
- `story_text` is converted to speech with gTTS and played with `st.audio()`
- Every scene (text + image + audio) is appended to `st.session_state.story_log`, so the entire story stays on screen across reruns instead of disappearing

### Phase 5 — Graceful Failures
- Every external call (Gemini, Pollinations, gTTS) is wrapped in `try...except`
- If the image server is busy, the app shows `st.toast("Image server is busy, skipping visual...")` and continues the story with no image, instead of crashing
- Same pattern for narration failures

---

## 🛠 Tech Stack

| Layer          | Technology |
|----------------|------------|
| Language       | Python 3.10+ |
| Framework      | Streamlit |
| Text Generation | Google Gemini API (`google-genai` SDK) |
| Image Generation | Pollinations.ai (free, no key) |
| Text-to-Speech | gTTS (Google Text-to-Speech) |
| Styling        | Custom CSS |

---

## 🔑 Getting a Free Gemini API Key

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with a Google account
3. Click **Create API Key** — no credit card required
4. Paste the key into the app's sidebar when running it

No key is needed for Pollinations.ai (image generation) or gTTS (narration) — only the story engine requires one.

---

## 📸 Screenshots

> Add screenshots to the `screenshots/` folder and reference them here.

| Story Settings | A Generated Scene |
|------------------|----------------------|
<img width="1917" height="883" alt="image" src="https://github.com/user-attachments/assets/b3713d55-a662-46b8-9ef1-810ce5933390" />
<img width="1917" height="917" alt="image" src="https://github.com/user-attachments/assets/88a4735e-3468-4b41-9fac-ffa9d20aa827" />
<img width="1917" height="816" alt="image" src="https://github.com/user-attachments/assets/3e3aad48-b516-45da-a24c-b84d1e1eb269" />


---

## 📂 Folder Structure

```
multimodal-visual-novel/
│
├── app.py              # Main Streamlit app — all 5 phases orchestrated here
├── utils.py               # Gemini/JSON, Pollinations, and gTTS helper functions
├── styles.css               # Cinematic dark theme
├── requirements.txt          # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                    # Git ignore rules
├── assets/                         # Icons / static assets
└── screenshots/                     # App screenshots for README
```

---

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/multimodal-visual-novel.git
cd multimodal-visual-novel
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On macOS/Linux
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
streamlit run app.py
```

Paste your Gemini API key into the sidebar, pick a genre and art style, and click **Begin Story**.

---

## 💻 Running in VS Code on Windows 11

1. Install [Python 3.10+](https://www.python.org/downloads/) (check "Add python.exe to PATH") and [VS Code](https://code.visualstudio.com/) with the Python extension.
2. Extract this project folder, e.g. to `C:\Projects\multimodal-visual-novel`.
3. `File → Open Folder...` in VS Code → select the folder.
4. Open the integrated terminal (`` Ctrl+` ``) — defaults to PowerShell.
5. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
   If PowerShell blocks the script, run once: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
6. `Ctrl+Shift+P` → **"Python: Select Interpreter"** → choose `.\venv\Scripts\python.exe`
7. Install dependencies: `pip install -r requirements.txt`
8. Run the app: `streamlit run app.py`

> Note: gTTS needs an internet connection to synthesize audio (it calls Google Translate's TTS endpoint under the hood) — this is expected and already handled gracefully if it's ever unreachable.

---

## ☁️ Deployment

### Streamlit Community Cloud
1. Push this project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app**, select your repo/branch, set the main file to `app.py`.
4. Deploy. Users paste their own Gemini API key into the sidebar at runtime.

### Render
1. Push this project to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

---

## ✅ Assignment Checklist

- [x] `@st.cache_resource` caches the Gemini client
- [x] Sidebar "Story Settings" with Genre and Art Style dropdowns
- [x] `st.session_state` stores chat history and the rendered story log
- [x] Gemini instructed via system prompt to return strict JSON (`story_text`, `image_prompt`, `options`)
- [x] `json` library parses the AI's string response into a Python dict
- [x] `for` loop dynamically generates an `st.button()` per option — no fixed `st.chat_input()`
- [x] Clicking a dynamic button sends that choice back to Gemini as the next move
- [x] `image_prompt` sent to Pollinations.ai and rendered on screen
- [x] `story_text` converted to speech via gTTS and played with `st.audio()`
- [x] Story text and image persist across reruns via `st.session_state`
- [x] All API calls wrapped in `try...except`; failures degrade gracefully via `st.toast()` instead of crashing

---

## 🔮 Future Improvements

- Save/load story sessions to continue later
- Branching story map visualization
- Character voice selection for narration
- Export the completed story as a shareable PDF or video

---

### 👤 Author

Built as the Capstone Mini-Project for the MirAI School of Technology Virtual Summer Internship 2026 — AI Builder Track.
