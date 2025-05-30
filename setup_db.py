import sqlite3
import bcrypt

# Opret forbindelse til databasen
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Opret en tabel til vidensbasen
cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL
)
""")

# Opret en tabel til brugere
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    can_search_web BOOLEAN NOT NULL DEFAULT FALSE
)
""")

# Tilføj nogle standard spørgsmål (valgfrit)
sample_data = [
    ("hvordan logger jeg ind?", "Du logger ind via portal.virksomhed.dk med din medarbejderkonto."),
    ("hvordan nulstiller jeg min adgangskode?", "Gå til 'Glemt adgangskode' på login-siden."),
    ("hvordan opretter jeg en ny faktura?", "Gå til faktureringsmodulet og klik på 'Ny faktura'.")
]

# Indsæt kun hvis de ikke allerede findes
for question, answer in sample_data:
    cursor.execute("INSERT OR IGNORE INTO knowledge_base (question, answer) VALUES (?, ?)", (question, answer))

# Tilføj en admin-bruger (kun hvis den ikke findes)
password = "admin123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

cursor.execute("""
INSERT OR IGNORE INTO users (username, hashed_password, role, can_search_web)
VALUES (?, ?, ?, ?)
""", ("admin", hashed, "admin", True))

# Gem ændringer og luk forbindelsen
conn.commit()
conn.close()

print("✅ Database oprettet, standard spørgsmål og admin-bruger tilføjet!")

