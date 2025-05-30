import sqlite3
import bcrypt

conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    can_search_web BOOLEAN NOT NULL DEFAULT FALSE
)
""")

sample_data = [
    ("hvordan logger jeg ind?", "Du logger ind via portal.virksomhed.dk med din medarbejderkonto."),
    ("hvordan nulstiller jeg min adgangskode?", "Gå til 'Glemt adgangskode' på login-siden."),
    ("hvordan opretter jeg en ny faktura?", "Gå til faktureringsmodulet og klik på 'Ny faktura'.")
]

for question, answer in sample_data:
    cursor.execute("INSERT OR IGNORE INTO knowledge_base (question, answer) VALUES (?, ?)", (question, answer))

password = "admin123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

cursor.execute("""
INSERT OR IGNORE INTO users (username, hashed_password, role, can_search_web)
VALUES (?, ?, ?, ?)
""", ("admin", hashed, "admin", True))

conn.commit()
conn.close()

print("✅ Database oprettet, standard spørgsmål og admin-bruger tilføjet!")

