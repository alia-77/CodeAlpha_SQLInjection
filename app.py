import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

from database import Base, engine, SessionLocal
from models import User, Employee
from auth import hash_password, verify_password, CAPABILITY_CODE
from security import encrypt, decrypt

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    admin = db.query(User).filter(
        User.username == "admin"
    ).first()

    if not admin:

        admin = User(
            username="admin",
            password=hash_password("admin123"),
            role="Admin"
        )

        db.add(admin)
        db.commit()

    db.close()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "CHANGE_THIS_TO_A_RANDOM_SECRET")
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


def current_user(request: Request):

    return request.session.get("user")


# LOGIN

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.post("/login")
def login(

    request: Request,

    username: str = Form(...),

    password: str = Form(...),

    capability_code: str = Form(...)

):

    if capability_code != CAPABILITY_CODE:

        return HTMLResponse(

            "<h2>Invalid capability code.</h2>",

            status_code=401

        )

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == username
    ).first()

    db.close()

    if not user:

        return HTMLResponse(
            "<h2>User not found.</h2>",
            status_code=401
        )

    if not verify_password(password, user.password):

        return HTMLResponse(
            "<h2>Incorrect password.</h2>",
            status_code=401
        )

    request.session["user"] = username

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )


# Dashboard

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    username = current_user(request)

    if not username:

        return RedirectResponse("/")

    db = SessionLocal()
    employees = db.query(Employee).all()
    data = []

    for employee in employees:

        data.append(

            {

                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "ssn": decrypt(employee.ssn),
                "salary": decrypt(employee.salary)

            }

        )

    db.close()

    return templates.TemplateResponse(

        request=request,
        name="dashboard.html",

        context={

            "username": username,
            "employees": data

        }

    )


# Add Employee

@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):

    if not current_user(request):

        return RedirectResponse("/")

    return templates.TemplateResponse(

        request=request,
        name="add_employee.html"

    )


@app.post("/add")
def add_employee(

    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    ssn: str = Form(...),
    salary: str = Form(...)

):

    if not current_user(request):

        return RedirectResponse("/")
    
    if "@" not in email or "." not in email.split("@")[-1]:

        return HTMLResponse(
            "<h2>Invalid email address.</h2>",
            status_code=400
        )

    db = SessionLocal()

    existing = db.query(Employee).all()

    for record in existing:

        if decrypt(record.ssn) == ssn:

            db.close()

            return HTMLResponse(
                "<h2>SSN already exists.</h2>",
                status_code=400
            )

    employee = Employee(

        name=name,
        email=email,
        ssn=encrypt(ssn),
        salary=encrypt(salary)

    )

    db.add(employee)
    db.commit()
    db.close()

    return RedirectResponse(

        "/dashboard",
        status_code=303

    )


# Delete

@app.get("/delete/{employee_id}")
def delete_employee(

    request: Request,

    employee_id: int

):

    if not current_user(request):

        return RedirectResponse("/")

    db = SessionLocal()

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee:

        db.delete(employee)
        db.commit()

    db.close()

    return RedirectResponse(

        "/dashboard",

        status_code=303

    )


# SQL Injection Demo

@app.get("/sql-demo", response_class=HTMLResponse)
def sql_demo(request: Request):

    if not current_user(request):

        return RedirectResponse("/")

    return templates.TemplateResponse(

        request=request,
        name="sql_demo.html"

    )


# LOGOUT

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/")

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):

    if not current_user(request):
        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "results": None,
            "query": ""
        }
    )


@app.post("/search", response_class=HTMLResponse)
def search(

    request: Request,
    query: str = Form(...)

):

    if not current_user(request):
        return RedirectResponse("/")

    db = SessionLocal()

    results = db.query(Employee).filter(
        Employee.name.ilike(f"%{query}%")
    ).all()

    employees = []

    for employee in results:

        employees.append({

            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "ssn": decrypt(employee.ssn),
            "salary": decrypt(employee.salary)

        })

    db.close()

    return templates.TemplateResponse(

        request=request,
        name="search.html",

        context={

            "query": query,
            "results": employees

        }

    )