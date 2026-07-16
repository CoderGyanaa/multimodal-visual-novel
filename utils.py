"""
utils.py
Helper functions for The Multi-Modal Visual Novel capstone.

Splits out of app.py for readability:
- Gemini structured-JSON scene generation
- Pollinations.ai image fetching
- gTTS narration synthesis
"""

import io
import json
import urllib.parse

import requests
from google import genai
from google.genai import types
from gtts import gTTS


class StoryError(Exception):
    """Raised when the Gemini call or JSON parsing fails."""
    pass


class ImageError(Exception):
    """Raised when the Pollinations.ai image request fails."""
    pass


class AudioError(Exception):
    """Raised when TTS narration synthesis fails."""
    pass


GENRES = [
    "Fantasy Adventure",
    "Sci-Fi Thriller",
    "Horror Mystery",
    "Cyberpunk Noir",
    "Fairy Tale",
    "Post-Apocalyptic Survival",
]

ART_STYLES = {
    "Photorealistic": "photorealistic, cinematic lighting, high detail, 8k",
    "Digital Art": "digital painting, vibrant colors, trending on artstation",
    "Anime": "anime style, studio ghibli inspired, cel shaded",
    "Oil Painting": "oil painting, textured brush strokes, classical art",
    "Watercolor": "watercolor illustration, soft edges, pastel tones",
    "Cyberpunk": "cyberpunk style, neon lights, futuristic, high contrast",
    "3D Render": "3d render, octane render, unreal engine, studio lighting",
    "Sketch": "pencil sketch, black and white, hand-drawn line art",
}

DEFAULT_MODEL = "gemini-3.1-flash-lite"


def build_system_prompt(genre: str) -> str:
    return (
        f"You are the narrator of an interactive '{genre}' visual novel. "
        "Continue an immersive story based on the player's chosen action "
        "(or begin a new one if this is the first turn). "
        "You must respond ONLY with a single valid JSON object — no markdown "
        "fences, no extra commentary — with EXACTLY these three keys:\n"
        '  "story_text": a vivid narrative paragraph, 3 to 5 sentences.\n'
        '  "image_prompt": a heavily descriptive, style-neutral prompt (in '
        "English, no character names) for an AI image generator depicting "
        "the current scene.\n"
        '  "options": a JSON array of 2 to 3 short, distinct strings '
        "describing the player's possible next actions.\n"
        "Do not include anything outside the JSON object."
    )


def get_gemini_client(api_key: str):
    """Creates a Gemini client. Wrapped with @st.cache_resource in app.py."""
    return genai.Client(api_key=api_key)


def generate_scene(client, genre: str, contents: list, model: str = DEFAULT_MODEL) -> dict:
    """
    Sends the conversation so far to Gemini and parses the structured JSON
    scene response into a dict with keys: story_text, image_prompt, options.
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(genre),
                response_mime_type="application/json",
                temperature=1.0,
            ),
        )
        if not response or not response.text:
            raise StoryError("The story engine returned an empty response.")
        raw_text = response.text
    except StoryError:
        raise
    except Exception as e:
        raise StoryError(f"Gemini API error: {e}")

    try:
        scene = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise StoryError(f"Could not parse the story JSON: {e}")

    for key in ("story_text", "image_prompt", "options"):
        if key not in scene:
            raise StoryError(f"Story JSON is missing the '{key}' key.")

    return scene


def fetch_scene_image(image_prompt: str, art_style: str, width: int = 768, height: int = 512, timeout: int = 45) -> bytes:
    """Fetches a generated image from Pollinations.ai for the current scene."""
    style_keywords = ART_STYLES.get(art_style, "")
    full_prompt = f"{image_prompt}, {style_keywords}" if style_keywords else image_prompt
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise ImageError(f"Image server request failed: {e}")

    if response.status_code != 200:
        raise ImageError(f"Image server returned status {response.status_code}")

    return response.content


def synthesize_narration(story_text: str) -> bytes:
    """Converts story_text to speech (MP3 bytes) using gTTS."""
    try:
        tts = gTTS(text=story_text, lang="en")
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        raise AudioError(f"TTS narration failed: {e}")
