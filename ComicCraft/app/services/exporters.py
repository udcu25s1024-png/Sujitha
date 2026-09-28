from datetime import datetime
from pathlib import Path
import re
import textwrap

from fpdf import FPDF

from app.config import settings
from app.models import ComicLayout
from app.services.storage import ensure_directories


def pdf_text(value: str) -> str:
    """
    Convert text to a format that the built-in
    Helvetica font can safely render.
    """
    value = value or ""

    value = (
        value.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\t", " ")
    )

    return (
        value.encode("latin-1", "replace")
        .decode("latin-1")
    )


def safe_pdf_text(value: str, width_chars: int = 80) -> str:
    """
    Prevent FPDF from failing when Gemini returns
    extremely long words or unbroken strings.
    """

    value = pdf_text(value)

    lines = []

    for original_line in value.split("\n"):
        original_line = original_line.strip()

        if not original_line:
            lines.append("")
            continue

        wrapped = textwrap.wrap(
            original_line,
            width=width_chars,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=True,
        )

        if wrapped:
            lines.extend(wrapped)
        else:
            lines.append("")

    return "\n".join(lines)


def add_text_block(
    pdf: FPDF,
    label: str,
    value: str,
):
    """
    Add a labelled text section safely.
    """

    pdf.set_x(15)

    pdf.set_font(
        "Helvetica",
        "B",
        11,
    )

    pdf.multi_cell(
        180,
        7,
        pdf_text(label),
    )

    pdf.set_x(15)

    pdf.set_font(
        "Helvetica",
        "",
        11,
    )

    safe_value = safe_pdf_text(value)

    pdf.multi_cell(
        180,
        7,
        safe_value,
    )

    pdf.ln(2)


def save_pdf(
    title: str,
    layout: list[ComicLayout],
) -> str:

    ensure_directories()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    slug = re.sub(
        r"[^A-Za-z0-9]+",
        "-",
        title.lower(),
    ).strip("-")

    slug = slug[:50]

    if not slug:
        slug = "comic"

    filename = f"{slug}_{timestamp}.pdf"

    output_path = (
        Path(settings.static_dir)
        / "exports"
        / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # -----------------------------
        # PANEL TITLE
        # -----------------------------

        pdf.set_x(15)

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        title_text = (
            f"Panel {panel.panel_number}: "
            f"{panel.title}"
        )

        pdf.multi_cell(
            180,
            10,
            safe_pdf_text(
                title_text,
                width_chars=65,
            ),
        )

        # -----------------------------
        # PANEL IMAGE
        # -----------------------------

        image_path = (
            Path(settings.static_dir)
            / "panels"
            / Path(panel.image_url).name
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=15,
                y=35,
                w=180,
                h=100,
                keep_aspect_ratio=True,
            )

            pdf.set_y(140)

        else:

            pdf.set_y(40)

            pdf.set_font(
                "Helvetica",
                "I",
                11,
            )

            pdf.multi_cell(
                180,
                7,
                "Image was not generated.",
            )

        # -----------------------------
        # SCENE DESCRIPTION
        # -----------------------------

        pdf.set_x(15)

        pdf.set_font(
            "Helvetica",
            "I",
            11,
        )

        pdf.multi_cell(
            180,
            7,
            safe_pdf_text(
                panel.scene_description
            ),
        )

        pdf.ln(2)

        # -----------------------------
        # CAPTION
        # -----------------------------

        add_text_block(
            pdf,
            "Caption:",
            panel.caption,
        )

        # -----------------------------
        # DIALOGUE
        # -----------------------------

        if panel.dialogue:

            add_text_block(
                pdf,
                "Dialogue:",
                panel.dialogue,
            )

        # -----------------------------
        # NARRATION
        # -----------------------------

        if panel.narration:

            add_text_block(
                pdf,
                "Narration:",
                panel.narration,
            )

    pdf.output(str(output_path))

    return str(output_path)