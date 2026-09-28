from pydantic import BaseModel,Field,field_validator
class PromptRequest(BaseModel):
    story_prompt:str=Field(min_length=5,max_length=2000); character_name:str=Field(min_length=1,max_length=80); setting:str=Field(min_length=1,max_length=120); tone:str=Field(min_length=1,max_length=60); art_style:str=Field(min_length=1,max_length=100)
    @field_validator('*')
    @classmethod
    def strip(cls,v): return v.strip()
class PanelOutline(BaseModel): panel_number:int; title:str; scene_description:str; image_prompt:str
class PanelStory(PanelOutline): caption:str; narration:str; dialogue:str
class ComicLayout(PanelStory): image_url:str
class ComicResponse(BaseModel): title:str; panels:list[ComicLayout]; pdf_url:str
