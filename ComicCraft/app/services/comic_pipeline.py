from pathlib import Path

from app.models import (
    ComicLayout,
    ComicResponse,
    PromptRequest,
)

from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.exporters import save_pdf


def generate_comic(
    payload: PromptRequest,
) -> ComicResponse:

    # ----------------------------------------
    # STEP 1: Generate comic outline
    # ----------------------------------------

    outline = generate_outline(payload)

    # ----------------------------------------
    # STEP 2: Generate detailed story
    # ----------------------------------------

    stories = generate_story(
        payload,
        outline,
    )

    if not stories:
        raise RuntimeError(
            "Gemini did not return any story panels."
        )

    # ----------------------------------------
    # STEP 3: Generate images
    # ----------------------------------------

    image_paths = []

    for panel in stories:

        prompt = (
            f"{panel.image_prompt}. "
            f"Comic panel {panel.panel_number}. "
            "Keep the main character visually "
            "consistent across all panels. "
            "Clean composition, strong focal point, "
            "family-friendly visual storytelling."
        )

        image_path = generate_image(
            prompt=prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(image_path)

    # ----------------------------------------
    # STEP 4: Convert PanelStory -> ComicLayout
    # ----------------------------------------

    layout: list[ComicLayout] = []

    for story, image_path in zip(
        stories,
        image_paths,
    ):

        filename = Path(image_path).name

        panel_layout = ComicLayout(
            panel_number=story.panel_number,
            title=story.title,
            image_url=f"/static/panels/{filename}",
            scene_description=story.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=story.image_prompt,
        )

        layout.append(panel_layout)

    # ----------------------------------------
    # STEP 5: Validate panel count
    # ----------------------------------------

    if len(layout) != len(stories):
        raise RuntimeError(
            "Comic layout creation failed."
        )

    # ----------------------------------------
    # STEP 6: Create comic title
    # ----------------------------------------

    title = (
        f"{payload.character_name}'s "
        "Comic Adventure"
    )

    # ----------------------------------------
    # STEP 7: Export PDF
    # ----------------------------------------

    pdf_path = save_pdf(
        title=title,
        layout=layout,
    )

    pdf_filename = Path(pdf_path).name

    # ----------------------------------------
    # STEP 8: Final response
    # ----------------------------------------

    return ComicResponse(
        title=title,
        panels=layout,
        pdf_url=(
            f"/static/exports/{pdf_filename}"
        ),
    )