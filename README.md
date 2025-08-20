# Gissa HTML – Skolprojekt

Detta är ett skolprojekt där eleverna får i uppgift att förbättra och vidareutveckla denna webbapplikation.

## Om projektet

Projektet är en Flask-baserad webbapp där användare kan gissa HTML-kod utifrån olika layouter. Det finns även ett admin-läge för att ladda upp nya layouter och hantera användare.

## Syfte

Syftet är att ge elever praktisk erfarenhet av:
- Python och Flask
- Webbprogrammering (HTML, CSS, JavaScript)
- Versionshantering och samarbete
- Problemlösning och kreativ utveckling

## Din uppgift

Du som elev ska:
- Förbättra funktionalitet, design eller användarupplevelse
- Lägga till nya features eller förbättra befintliga
- Skriva tydlig och läsbar kod
- Dokumentera dina ändringar


Se `install.txt` och/eller kör `start_app.bat` för att starta projektet lokalt.

## Standardinloggning (admin)

När du startar projektet första gången finns dessa konton:

- **Admin**
	- Användarnamn: `admin`
	- Lösenord: `admin123`
- **Superadmin**
	- Användarnamn: `superadmin`
	- Lösenord: `superadmin123`

Du kan ändra eller ta bort dessa i `admins.json`.

## Projektstruktur

**Huvudmappar och filer:**

- `app.py` – Huvudfilen med all serverlogik (Flask-applikationen).
- `requirements.txt` – Lista på Python-paket som behövs.
- `install.txt` – Steg-för-steg-guide för att installera och starta projektet.
- `start_app.bat` – Windows-script för att automatiskt starta projektet.
- `admins.json` – Innehåller admin-användare och lösenord (hashade).
- `layouts.json` – Innehåller alla uppladdade layouter, HTML-svar och ledtrådar.
- `process.log` och `stuff.txt` – (Valfria/extra filer, kan användas för loggning eller anteckningar).

**Mappar:**

- `static/` – Innehåller statiska filer som CSS och bilder.
	- `style.css` – All styling för sidan.
	- `layouts/` – Här sparas alla uppladdade layout-bilder (t.ex. 1.jpg, 2.jpg ...).

- `templates/` – Innehåller alla HTML-mallar (Jinja2) som används av Flask.
	- `base.html` – Grundlayout för alla sidor.
	- `index.html` – Startsidan.
	- `layout.html` – Sidan där man gissar HTML.
	- `upload.html` – Sida för att ladda upp nya layouter.
	- `admin.html` – Adminpanel för att hantera layouter.
	- `admin_users.html` – Adminpanel för att hantera användare.
	- `login.html` – Inloggningssida för admin.

## Tips
- Läs igenom koden i `app.py` och mallarna i `templates/`.
- Testa att logga in som admin (se instruktioner i `install.txt`).
- Använd gärna Git för versionshantering.

## Lycka till!

> Detta projekt är endast för utbildningssyfte och ska inte användas i produktion utan vidare säkerhetsgranskning.
