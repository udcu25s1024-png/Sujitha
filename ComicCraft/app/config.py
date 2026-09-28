from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR=Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    gemini_api_key:str=''; hf_api_key:str=''; gemini_outline_model:str='gemini-2.5-flash'; gemini_story_model:str='gemini-2.5-pro'; hf_image_model:str='stabilityai/stable-diffusion-3-medium-diffusers'; hf_provider:str='auto'; image_provider:str='placeholder'; comic_panels:int=5
    static_dir:str=str(BASE_DIR/'static'); templates_dir:str=str(BASE_DIR/'templates')
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
settings=Settings()
