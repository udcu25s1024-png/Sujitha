import json

from google import genai
from google.genai import types

from app.config import settings
from app.models import PanelOutline, PanelStory, PromptRequest


def get_gemini_client():
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Please add it to your .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(
    payload: PromptRequest,
    outline: list[PanelOutline],
) -> list[PanelStory]:

    client = get_gemini_client()

    outline_json = json.dumps(
        [panel.model_dump() for panel in outline],
        ensure_ascii=False,
    )

    prompt = f"""
You are the comic script writer for ComicCraft.

Create a complete comic script from the supplied panel outline.

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

PANEL OUTLINE:

{outline_json}

TASK

Expand every panel into:

- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

IMPORTANT

1. Keep the story coherent from panel 1 through panel {settings.comic_panels}.
2. Keep the main character visually and narratively consistent.
3. Dialogue should be short enough for a comic panel.
4. Narration should explain important actions and events.
5. Image prompts should describe:
   - characters
   - environment
   - action
   - lighting
   - composition
   - visual style
6. Do not introduce real people.
7. Keep the content family-friendly.
8. Avoid:
   - hateful content
   - explicit sexual content
   - sexual content involving minors
   - graphic gore
   - criminal instructions

RETURN ONLY VALID JSON.

Return exactly this structure:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "Panel title",
            "scene_description": "Scene description",
            "caption": "Short caption",
            "narration": "Narration",
            "dialogue": "Dialogue",
            "image_prompt": "Detailed image generation prompt"
        }}
    ]
}}

Do not add markdown.
Do not add ```json.
Do not add explanations.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=6000,
            response_mime_type="application/json",
        ),
    )

    try:
        raw_text = response.text.strip()

        data = json.loads(raw_text)

        # Gemini may return:
        # {"panels": [...]}
        # OR directly [...]
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
                "Gemini story JSON does not contain a valid "
                "'panels' list."
            )

        stories = [
            PanelStory.model_validate(panel)
            for panel in panel_data
        ]

    except Exception as exc:
        raise RuntimeError(
            "Invalid Gemini story JSON: "
            f"{exc}"
        ) from exc

    if len(stories) != len(outline):
        raise RuntimeError(
            "Gemini story output does not contain the "
            f"expected {len(outline)} panels. "
            f"Received {len(stories)} panels."
        )

    return stories