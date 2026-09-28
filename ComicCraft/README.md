# ComicCraft

Open this folder in VS Code.

Windows setup:
1. Install Python 3.11+ and add Python to PATH.
2. Terminal: `python -m venv .venv`
3. `\.venv\Scripts\Activate.ps1`
4. `python -m pip install --upgrade pip`
5. `pip install -r requirements.txt`
6. Edit `.env` and add GEMINI_API_KEY.
7. Run `uvicorn app.main:app --reload`
8. Open http://127.0.0.1:8000

Default IMAGE_PROVIDER=placeholder lets you test without Hugging Face images. For real image generation, set IMAGE_PROVIDER=huggingface and add HF_API_KEY.
Tests: `pytest -q`
