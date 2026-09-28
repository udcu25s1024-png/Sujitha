from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routes import router
from app.services.storage import ensure_directories
ensure_directories(); app=FastAPI(title='ComicCraft',version='1.0.0'); app.mount('/static',StaticFiles(directory=settings.static_dir),name='static'); app.include_router(router)
@app.get('/health')
async def health(): return {'status':'ok','application':'ComicCraft','version':'1.0.0'}
