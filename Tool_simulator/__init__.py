from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND, HTTP_403_FORBIDDEN
import models
from auth import register_user, verify_password, get_password_hash
from database import SessionLocal
from tool_life_simulator import simulate_tool_life
from models import Simulation
import shutil
import os
from dotenv import load_dotenv
from fastapi import status

# Explicitly load your admin.env file
load_dotenv("admin.env")

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_sessions = {}

def get_current_user(request: Request, db: Session):
    username = user_sessions.get(request.client.host)
    if not username:
        return None
    return db.query(models.User).filter(models.User.username == username).first()

def is_admin(user: models.User):
    return user and user.is_admin

@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    username = user_sessions.get(request.client.host)
    user = None
    current_user = None
    if username:
        user = username
        current_user = db.query(models.User).filter(models.User.username == username).first()
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "current_user": current_user})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    if not user.is_approved:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Account pending admin approval"})
    user_sessions[request.client.host] = username
    return RedirectResponse("/", status_code=HTTP_302_FOUND)

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        register_user(db, username, password)
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)
    except:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})

@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not is_admin(user):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access Denied")
    users = db.query(models.User).all()
    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users, "current_user": user})

@router.post("/admin/approve/{user_id}")
def approve_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not is_admin(user):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access Denied")
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        target_user.is_approved = True
        db.commit()
    return RedirectResponse("/admin", status_code=HTTP_302_FOUND)

@router.post("/admin/make_admin/{user_id}")
def make_admin(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not is_admin(user):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access Denied")
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        target_user.is_admin = True
        db.commit()
    return RedirectResponse("/admin", status_code=HTTP_302_FOUND)

@router.post("/admin/revoke_admin/{user_id}")
def revoke_admin(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not is_admin(user):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access Denied")
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        target_user.is_admin = False
        db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_302_FOUND)  # Fixed

@router.post("/admin/unapprove/{user_id}")
def unapprove_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not is_admin(user):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access Denied")
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        target_user.is_approved = False
        db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_302_FOUND)  # Fixed

@router.post("/simulate/", response_class=HTMLResponse)
def simulate(
    request: Request,
    planner_name: str = Form(...),
    pieces: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = user_sessions.get(request.client.host)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    output_filename, result = simulate_tool_life(file_path, planner_name, pieces)
    os.remove(file_path)
    user_id = db.query(models.User).filter(models.User.username == user).first().id
    sim = Simulation(planner_name=planner_name, filename=output_filename, user_id=user_id)
    db.add(sim)
    db.commit()
    return templates.TemplateResponse("result.html", {
        "request": request,
        "result": result,
        "output_filename": output_filename
    })

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("results", filename)
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')

@router.get("/component/{component_name}", response_class=HTMLResponse)
def view_component(request: Request, component_name: str):
    return templates.TemplateResponse("component_view.html", {"request": request, "component": component_name})

@router.post("/logout")
def logout(request: Request):
    user_sessions.pop(request.client.host, None)
    response = RedirectResponse("/", status_code=HTTP_302_FOUND)
    # Invalidate browser cache for security (see below)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@router.on_event("startup")
def initialize_admin():
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_username or not admin_password:
            raise ValueError("Admin credentials missing in admin.env file")
        admin_exists = db.query(models.User).filter(
            models.User.username == admin_username,
            models.User.is_admin == True
        ).first()
        if not admin_exists:
            admin = models.User(
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                is_admin=True,
                is_approved=True
            )
            db.add(admin)
            db.commit()
            print("Initial admin user created")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Admin initialization error: {str(e)}")
    finally:
        db.close()
