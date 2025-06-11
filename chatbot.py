from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from duckduckgo_search import DDGS
from typing import List
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import psycopg2
import bcrypt
import requests
import os

load_dotenv()

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

user_contexts = {}


SECRET_KEY = os.getenv("SECRET_KEY", "meget-hemmelig-nøgle")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, can_search_web FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "id": row[0],
            "username": row[1],
            "role": row[2],
            "can_search_web": bool(row[3])
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class Query(BaseModel):
    question: str = Field(..., min_length=1, max_length=100)
    answer: str = None

class ChatPayload(BaseModel):
    question: str
    confirm_external: bool = False

class UserPermission(BaseModel):
    username: str
    can_search_web: bool

class PermissionUpdateRequest(BaseModel):
    users: List[UserPermission]

@limiter.limit("5/minute")
@app.post("/token")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, hashed_password FROM users WHERE username = %s", (form_data.username.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    hashed_pw = row[1]
    if isinstance(hashed_pw, str):
        hashed_pw = hashed_pw.encode("utf-8")

    if not bcrypt.checkpw(form_data.password.encode("utf-8"), hashed_pw):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

def get_answer_from_db(user_question):
    MINIMUM_SCORE = 4
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM knowledge_base")
    results = cursor.fetchall()
    conn.close()

    input_words = set(user_question.lower().rstrip("?").split())
    best_score = 0
    best_answer = None
    for db_question, db_answer in results:
        db_words = set(db_question.lower().split())
        score = len(input_words.intersection(db_words))
        if score > best_score:
            best_score = score
            best_answer = db_answer
    return best_answer if best_score >= MINIMUM_SCORE else None

def search_serper(query):
    api_key = "6d2226b7232202889b6904bf3c0df1f7f8031d5d"
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {"q": query}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()
        if "organic" in results and results["organic"]:
            top_result = results["organic"][0]
            return f"""{top_result['snippet']}<br><a href="{top_result['link']}" target="_blank">🔗 {top_result['title']}</a>"""
        return "Jeg kunne ikke finde noget svar lige nu."
    except Exception as e:
        print("Serper fejl:", e)
        return "Fejl ved websøgning."

def log_interaction(username, question, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (username, question, answer) VALUES (%s, %s, %s)",
        (username, question, answer)
    )
    conn.commit()
    conn.close()


@limiter.limit("10/minute")
@app.post("/chat")
def chat(request: Request, payload: ChatPayload, user: dict = Depends(get_current_user)):
    username = user["username"]
    context = []
    user_contexts[username] = context
    user_question = payload.question.strip()
    context.append({"role": "user", "content": user_question})
    internal_answer = get_answer_from_db(user_question)

    if internal_answer:
        answer = internal_answer
        context.append({"role": "assistant", "content": answer})
        log_interaction(username, user_question, answer)
        return {"answer": answer}

    if not payload.confirm_external:
        return JSONResponse(content={
            "require_confirmation": True,
            "response": "⚠️ Du er ved at foretage en websøgning uden for det interne system."
        })

    answer = search_serper(user_question)
    context.append({"role": "assistant", "content": answer})
    log_interaction(username, user_question, answer)
    return {"answer": answer}

@app.post("/add_question")
def add_question(query: Query, user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)", (query.question.lower(), query.answer))
    conn.commit()
    conn.close()
    return {"message": "Spørgsmål tilføjet!"}

@app.get("/my_logs")
def get_my_logs(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, question, answer FROM logs WHERE username = %s ORDER BY timestamp DESC", (user["username"],))
    rows = cursor.fetchall()
    conn.close()
    return {"logs": [{"timestamp": row[0], "question": row[1], "answer": row[2]} for row in rows]}

@app.get("/admin/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Adgang nægtet")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, can_search_web FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": r[0], "role": r[1], "can_search_web": bool(r[2])} for r in rows]

@app.post("/admin/update_web_access")
def update_web_access(data: PermissionUpdateRequest, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Adgang nægtet")

    conn = get_db_connection()
    cursor = conn.cursor()

    for user in data.users:
        cursor.execute(
            "UPDATE users SET can_search_web = %s WHERE username = %s",
            (user.can_search_web, user.username)
        )

    conn.commit()
    conn.close()

    return {"message": "Webadgange opdateret"}


@app.get("/admin/logs", response_class=HTMLResponse)
async def show_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    html = """
    <html>
        <head>
            <title>Seneste logs</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Seneste logs</h1>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Brugernavn</th>
                    <th>Spørgsmål</th>
                    <th>Svar</th>
                    <th>Timestamp</th>
                </tr>
    """
    for row in rows:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"

    html += """
            </table>
        </body>
    </html>
    """
    return html

@app.get("/admin/feedback", response_class=HTMLResponse)
async def show_feedback():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    html = """
    <html>
        <head>
            <title>Feedbackoversigt</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Feedbackoversigt</h1>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Brugernavn</th>
                    <th>Spørgsmål</th>
                    <th>Nyttigt?</th>
                    <th>Timestamp</th>
                </tr>
    """
    for row in rows:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"

    html += """
            </table>
        </body>
    </html>
    """
    return html


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    html = """
    <html>
        <head>
            <title>Admin Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 30px; }
                a { display: block; margin: 15px 0; font-size: 18px; }
            </style>
        </head>
        <body>
            <h1>Admin Dashboard</h1>
            <a href="/admin/logs">📄 Se seneste logs</a>
            <a href="/admin/feedback">⭐ Se bruger-feedback</a>
        </body>
    </html>
    """
    return html


@app.get("/health")
def health_check():
    return {"message": "Effi er klar 🚀"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000)


