import threading
import webview
from fastapi import FastAPI,Request, UploadFile, File, Query
import uvicorn
import time
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import sys
import os
from app.task.import_task import import_profile_task
from app.task.gettoken_task import gettoken_profile_task
from fastapi.staticfiles import StaticFiles
from app.task.startprofile_task import startprofile_task
from app.task.paginate_task import paginate_task
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.task.login_task import login_task  
from app.task.logout_action import logout_task
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# app = Flask(__name__)
# CORS(app)
app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.abspath(".")

def get_templates_path():
    return os.path.join(get_base_path(), 'templates')

def get_static_path():
    return os.path.join(get_base_path(), 'static')


# app = FastAPI()
templates = Jinja2Templates(directory=get_templates_path())
app.mount("/static", StaticFiles(directory=get_static_path()), name="static")



@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login__action')
async def login__action(request: Request):
    body = await request.json()
    username=body.get('username')
    password=body.get('password')
    return login_task(request, username, password)

@app.post('/logout__action')
async def logout__action(request: Request):
    return logout_task(request)

@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/import_profile__action', response_class=HTMLResponse)
async def import_profile_action(file: UploadFile = File(...)):
    return await import_profile_task(file)

@app.post('/get_token__action')
async def get_token_action(request: Request):
    return await gettoken_profile_task(request)


@app.post('/start__action')
async def start__action(request: Request):
    return await startprofile_task(request)

@app.get('/pushcode__action', response_class=HTMLResponse)
async def pushcode__action(request: Request):
    return templates.TemplateResponse("popup.html", {"request": request})

@app.get('/paginate_page/{page}')
async def paginate_page(request: Request, page:int, total:int = Query(13), limit:int = Query(13)):
    return paginate_task(request, page, total, limit)



def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=5500)
def run_playwright():
    uvicorn.run(app, host="127.0.0.1", port=8800)


if __name__ == "__main__":
    
    print("Starting FastAPI server...")  # Debugging: print a message when the server starts
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    threading.Thread(target=run_playwright, daemon=True).start()

    time.sleep(1)

    webview.create_window("Get Token", "http://127.0.0.1:5500",width=1400, height=1000)
    webview.start()

