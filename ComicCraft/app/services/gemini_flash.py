import json

from google import genai
from google.genai import types

from app.config import settings
from app.models import PanelOutline, PromptRequest


def get_gemini_client():
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Please add it to your .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(payload: PromptRequest) -> list[PanelOutline]:
    client = get_gemini_client()

    prompt = f"""
You are the comic outline planner for ComicCraft.

Create exactly {settings.comic_panels} sequential comic panels.

USER INFORMATION

Story prompt:
{payload.story_prompt}

Main character:
{payload.character_name}

Setting:
{payload.setting}

Tone:
{payload.tone}

Art style:
{payload.art_style}

REQUIREMENTS

1. Create exactly {settings.comic_panels} panels.
2. The story must have:
   - beginning
   - development
   - climax
   - ending
3. Every panel must advance the story.
4. Every panel must have a visually distinct scene.
5. Maintain the same main character throughout.
6. Every image prompt must contain enough visual information
   for an image generation model.
7. Keep the content family-friendly.
8. Do not include:
   - hate speech
   - explicit sexual content
   - sexual content involving minors
   - graphic gore
   - instructions for criminal wrongdoing

IMPORTANT:
Return ONLY valid JSON.

Return the JSON as an object using exactly this format:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "Panel title",
            "scene_description": "Scene description",
            "image_prompt": "Detailed visual prompt"
        }}
    ]
}}

Do not add markdown.
Do not add ```json.
Do not add explanations.
"""

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=3000,
            response_mime_type="application/json",
        ),
    )

    try:
        raw_text = response.text.strip()

        data = json.loads(raw_text)

        # Gemini may sometimes return the panels directly
        # as a JSON list instead of {"panels": [...]}
        if isinstance(data, list):
            panel_data = data

        elif isinstance(data, dict):
            panel_data = data.get("panels")

        else:
            raise ValueError(
                "Gemini returned an unsupported JSON structure."
            )

        if not isinstance(panel_data, list):
            raise ValueError(
                "Gemini JSON does not contain a valid 'panels' list."
            )

        panels = [
            PanelOutline.model_validate(panel)
            for panel in panel_data
        ]

    except Exception as exc:
        raise RuntimeError(
            "Invalid Gemini outline JSON: "
            f"{exc}"
        ) from exc

    if len(panels) != settings.comic_panels:
        raise RuntimeError(
            f"Expected {settings.comic_panels} panels "
            f"but Gemini returned {len(panels)}."
        )

    return panels