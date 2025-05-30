import sqlite3

conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

qa_pairs = [
    ("Hvordan nulstiller jeg min adgangskode?", "Du kan nulstille adgangskoden via IT-portalen under 'Adgangskodeadministration'."),
    ("Hvad gør jeg, hvis printeren ikke virker?", "Tjek først strøm og forbindelser. Genstart derefter printeren og din computer."),
    ("Hvordan booker jeg en forsendelse?", "Log ind i speditørportalen og udfyld formularen for booking."),
    ("Hvad er trackingnummeret?", "Trackingnummer er det unikke ID, du får ved afsendelse. Du finder det i ordrebekræftelsen."),
    ("Hvordan åbner jeg et supportticket?", "Gå ind på supportsiden og klik på 'Ny sag' for at oprette et ticket."),
    ("Min computer starter ikke, hvad gør jeg?", "Tjek om strømforsyningen er tilsluttet og prøv at genstarte. Kontakt IT, hvis problemet fortsætter."),
    ("Hvordan installerer jeg printeren?", "Gå til 'Enheder' → 'Printere og scannere' og vælg 'Tilføj en printer'."),
    ("Hvordan får jeg adgang til fjernsupport?", "Kontakt IT og få tilsendt et TeamViewer-link eller et andet fjernsupportværktøj."),
    ("Jeg kan ikke tilgå netværket – hvad gør jeg?", "Tjek kabelforbindelse eller Wi-Fi, og genstart routeren. Kontakt IT ved vedvarende problemer."),
    ("Hvordan opdaterer jeg Windows?", "Gå til 'Indstillinger' → 'Opdatering og sikkerhed' → 'Windows Update'."),
    ("Hvordan ændrer jeg min skærmopløsning?", "Højreklik på skrivebordet → 'Skærmindstillinger' → Justér opløsningen."),
    ("Hvordan opretter jeg en e-mail signatur?", "I Outlook: Gå til 'Filer' → 'Indstillinger' → 'Mail' → 'Signaturer'."),
    ("Mit tastatur skriver forkerte tegn – hvad gør jeg?", "Tjek at sprogindstillingen er sat til 'Dansk' under 'Indstillinger' → 'Sprog'."),
    ("Hvordan installerer jeg software på firmacomputeren?", "Kontakt IT-afdelingen – der kan være krav om administratorrettigheder."),
    ("Hvordan tilslutter jeg mig virksomhedens VPN?", "Du skal bruge VPN-klienten og logge ind med dine medarbejderoplysninger. Kontakt IT for opsætning."),
    ("Hvordan skifter jeg adgangskode i Windows?", "Tryk Ctrl+Alt+Delete og vælg 'Skift adgangskode'."),
    ("Min mus reagerer ikke – hvad gør jeg?", "Tjek batteri, forbindelsestype og genstart computeren."),
    ("Hvordan tilføjer jeg en netværksdreven mappe?", "Højreklik i Stifinder → 'Tilføj netværksplacering' og angiv stien."),
    ("Hvordan laver jeg en skærmoptagelse?", "I Windows: Brug Windows+G for at åbne Xbox Game Bar."),
    ("Hvordan undgår jeg phishing-mails?", "Undlad at klikke på links i mistænkelige e-mails og kontakt IT ved tvivl."),
    ("Kan jeg bruge min egen enhed på netværket?", "Det afhænger af virksomhedens BYOD-politik – spørg IT."),
    ("Hvordan installerer jeg Teams?", "Du kan hente det fra Microsofts officielle hjemmeside eller via Office-portalen."),
    ("Hvordan laver jeg en systemgendannelse?", "Gå til 'Kontrolpanel' → 'Gendannelse' → 'Åbn Systemgendannelse'."),
    ("Hvordan tømmer jeg papirkurven automatisk?", "Aktiver Storage Sense i 'Indstillinger' → 'System' → 'Lagring'."),
    ("Hvordan opsætter jeg to skærme?", "Højreklik på skrivebordet → 'Skærmindstillinger' → 'Registrer' og konfigurer layout."),
    ("Hvordan aktiverer jeg mørk tilstand i Windows?", "Gå til 'Indstillinger' → 'Personliggørelse' → 'Farver' og vælg 'Mørk' som app-tilstand."),
    ("Hvordan finder jeg min IP-adresse?", "Åbn Kommandoprompt og skriv `ipconfig`."),
    ("Hvordan lukker jeg programmer, der ikke svarer?", "Tryk Ctrl+Shift+Esc for at åbne Jobliste og afslut programmet."),
    ("Hvordan renser jeg midlertidige filer?", "Kør 'Diskoprydning' via Start-menuen."),
    ("Hvordan gendanner jeg slettede filer?", "Tjek Papirkurven eller brug et gendannelsesværktøj som Recuva."),
    ("Hvordan deler jeg en fil via OneDrive?", "Højreklik på filen → 'Del' → vælg indstillinger og kopier link."),
    ("Hvordan nulstiller jeg netværksindstillinger?", "Gå til 'Indstillinger' → 'Netværk og internet' → 'Nulstil netværk'."),
    ("Min printer virker ikke – hvad gør jeg?", "Tjek forbindelsen, genstart printeren og installer drivere om nødvendigt."),
    ("Hvordan laver jeg en skærmklip?", "Tryk Windows+Shift+S for at bruge værktøjet 'Skærmklip'.")
]

for question, answer in qa_pairs:
    cursor.execute("SELECT 1 FROM knowledge_base WHERE question = ?", (question,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO knowledge_base (question, answer) VALUES (?, ?)", (question, answer))

conn.commit()
conn.close()
print("Nye spørgsmål er nu tilføjet – uden at overskrive de gamle.")

