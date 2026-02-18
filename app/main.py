# Copyright (c) 2026 Xist.GG LLC

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
from app import storage, crypto

from contextlib import asynccontextmanager
import asyncio

async def run_cleanup_loop():
    while True:
        try:
            # Run cleanup in thread pool to avoid blocking
            await asyncio.to_thread(storage.cleanup)
        except Exception:
            pass
        await asyncio.sleep(3600)  # Run every hour

@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.init_storage()
    cleanup_task = asyncio.create_task(run_cleanup_loop())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Burnar", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.post("/create", response_class=HTMLResponse)
async def create_secret(request: Request, content: str = Form(...)):
    key = crypto.generate_key()
    secret_uuid = str(uuid.uuid4())
    
    encrypted_content = crypto.encrypt(content, key)
    storage.save(secret_uuid, encrypted_content)
    
    # Generate link with fragment for key
    secret_url = request.url_for('view_secret', uuid=secret_uuid)
    full_link = f"{secret_url}#{key}"
    
    return templates.TemplateResponse(request=request, name="link.html", context={"link": full_link})

@app.get("/secret/{uuid}", response_class=HTMLResponse, name="view_secret")
async def view_secret(request: Request, uuid: str):
    if not storage.exists(uuid):
        return templates.TemplateResponse(request=request, name="error.html", context={"message": "Secret not found or already burned."})
    return templates.TemplateResponse(request=request, name="reveal.html", context={"uuid": uuid})

@app.post("/secret/{uuid}", response_class=HTMLResponse)
async def reveal_secret(request: Request, uuid: str, key: str = Form(...)):
    encrypted_data = storage.load(uuid)
    
    # Delete immediately (Burn)
    storage.delete(uuid)
    
    if not encrypted_data:
         return templates.TemplateResponse(request=request, name="error.html", context={"message": "Secret not found or already burned."})
    
    try:
        decrypted_content = crypto.decrypt(encrypted_data, key)
    except Exception:
        return templates.TemplateResponse(request=request, name="error.html", context={"message": "Invalid key or data corruption."})
        
    return templates.TemplateResponse(request=request, name="secret.html", context={"content": decrypted_content})
