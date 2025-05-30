import sqlite3

# Opret (eller åbn) databasen
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Opret tabel til vidensbase, hvis den ikke allerede findes
cursor.execute('''
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL
)
''')

# Gem ændringer og luk forbindelsen
conn.commit()
conn.close()

def insert_data():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Indsæt spørgsmål og svar
    data = [
        ("hvordan logger jeg ind", "Du logger ind via portal.virksomhed.dk med din medarbejderkonto."),
        ("hvordan nulstiller jeg min adgangskode", "Gå til 'Glemt adgangskode' på login-siden og følg instruktionerne."),
        ("hvordan opretter jeg en ny faktura", "Gå til faktureringsmodulet og klik på 'Ny faktura'. Udfyld detaljer og gem.")
    ]

    cursor.executemany("INSERT OR IGNORE INTO knowledge_base (question, answer) VALUES (?, ?)", data)

    conn.commit()
    conn.close()

insert_data()
