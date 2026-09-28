from pathlib import Path
from fastapi import APIRouter,Form,HTTPException,Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.models import PromptRequest
from app.services.comic_pipeline import generate_comic
from app.services.image_generator import generate_image
from app.services.storage import safe_filename
router=APIRouter(); templates=Jinja2Templates(directory=settings.templates_dir)
@router.get('/',response_class=HTMLResponse)
async def home(request:Request): return templates.TemplateResponse(request=request,name='index.html',context={})
@router.post('/generate',response_class=HTMLResponse)
async def generate(request:Request,story_prompt:str=Form(...),character_name:str=Form(...),setting:str=Form(...),tone:str=Form(...),art_style:str=Form(...)):
    try: comic=generate_comic(PromptRequest(story_prompt=story_prompt,character_name=character_name,setting=setting,tone=tone,art_style=art_style))
    except Exception as e: return templates.TemplateResponse(request=request,name='error.html',context={'error':str(e)},status_code=500)
    return templates.TemplateResponse(request=request,name='comic_preview.html',context={'comic':comic.model_dump()})
@router.post('/generate-comic/json')
async def generate_json(payload:PromptRequest):
    try:return JSONResponse(content=generate_comic(payload).model_dump())
    except Exception as e:raise HTTPException(500,detail=str(e)) from e
@router.get('/export-success',response_class=HTMLResponse)
async def export_success(request:Request,filename:str):
    f=safe_filename(filename); p=Path(settings.static_dir)/'exports'/f
    if not p.exists(): raise HTTPException(404,'PDF export not found.')
    return templates.TemplateResponse(request=request,name='export_success.html',context={'pdf_url':f'/static/exports/{f}'})
@router.get('/test-image')
async def test_image(prompt='A friendly fox in an enchanted forest, comic book illustration'):
    try: p=generate_image(prompt,0); return {'status':'ok','image_url':f'/static/panels/{Path(p).name}'}
    except Exception as e: raise HTTPException(500,detail=str(e)) from e
