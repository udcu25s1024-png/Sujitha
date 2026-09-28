from pathlib import Path

from PIL import Image, ImageDraw
from huggingface_hub import InferenceClient

from app.config import settings
from app.services.storage import ensure_directories


def create_placeholder_image(
    prompt: str,
    panel_number: int,
    output_path: Path,
) -> None:

    image = Image.new(
        "RGB",
        (1024, 1024),
        "#eeeeee",
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        (20, 20, 1004, 1004),
        outline="black",
        width=10,
    )

    # Header
    draw.text(
        (60, 60),
        f"COMICCRAFT - PANEL {panel_number}",
        fill="black",
    )

    # Placeholder message
    draw.text(
        (60, 150),
        "AI IMAGE PLACEHOLDER",
        fill="black",
    )

    # Prompt
    prompt_text = prompt[:500]

    draw.multiline_text(
        (60, 250),
        prompt_text,
        fill="black",
        spacing=12,
    )

    image.save(
        output_path,
        "PNG",
    )


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    ensure_directories()

    output_path = (
        Path(settings.static_dir)
        / "panels"
        / f"panel_{panel_number}.png"
    )

    # ----------------------------------------
    # PLACEHOLDER MODE
    # ----------------------------------------

    if settings.image_provider.lower() == "placeholder":

        create_placeholder_image(
            prompt=prompt,
            panel_number=panel_number,
            output_path=output_path,
        )

        return str(output_path)

    # ----------------------------------------
    # HUGGING FACE MODE
    # ----------------------------------------

    if not settings.hf_api_key:
        raise RuntimeError(
            "HF_API_KEY is not configured. "
            "Add it to your .env file or use "
            "IMAGE_PROVIDER=placeholder."
        )

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_api_key,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )

    image.save(
        output_path,
        "PNG",
    )

    return str(output_path)