# Kalendarz-App - Python Calendar Planner

Nowoczesna aplikacja kalendarza/planera napisana w Pythonie z Flask i interfejsem webowym.

## Funkcjonalności

- **Widok kalendarza** - intuicyjny miesięczny widok kalendarza
- **Planowanie godzinowe** - zaznaczanie konkretnych godzin
- **Dodawanie wydarzeń** - tworzenie i edycja zadań/spotkań
- **Wyszukiwanie** - szybkie znajdowanie wydarzeń
- **Lokalna baza danych** - SQLite do przechowywania danych
- **Interfejs webowy** - dostępny przez przeglądarkę na localhost


<img width="1470" height="839" alt="Zrzut ekranu 2025-07-23 o 12 44 56" src="https://github.com/user-attachments/assets/99955bcf-35b6-431d-80f7-49756b5d2e5e" />

<img width="1470" height="838" alt="Zrzut ekranu 2025-07-23 o 12 45 08" src="https://github.com/user-attachments/assets/66e6ba72-f3ea-4fba-a66b-3b3f4c651f3c" />



## Wymagania

- Python 3.7+
- Flask
- SQLAlchemy
- Flask-SQLAlchemy

## Instalacja i uruchomienie

1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Uruchom aplikację:
```bash
python main.py
```

3. Otwórz przeglądarkę i przejdź do:
```
http://localhost:5001
```

## Struktura projektu

```
kalendarz-app/
├── main.py # Główny plik aplikacji Flask
├── eventmenager.py
├── database.py             
├── templates/
│   └── calendar.html    # Szablon HTML kalendarza
├── static/
│   ├── css/
│   │   └── style.css    # Style CSS
│   └── js/
│       └── script.js    # JavaScript frontend
├── requirements.txt     # Zależności projektu
└── calendar.db         # Baza danych (tworzona automatycznie)
```

## Użytkowanie

### Podstawowe funkcje:
1. **Nawigacja po kalendarzu** - użyj strzałek lub przycisku "Dzisiaj"
2. **Wybór dnia** - kliknij na konkretny dzień w kalendarzu
3. **Dodawanie wydarzeń** - kliknij "Dodaj wydarzenie" lub użyj Ctrl+N
4. **Edycja/usuwanie** - kliknij na wydarzenie i wybierz akcję
5. **Wyszukiwanie** - użyj przycisku wyszukiwania lub Ctrl+F

### Skróty klawiszowe:
- `Ctrl+N` - Dodaj nowe wydarzenie
- `Ctrl+F` - Otwórz wyszukiwanie
- `Esc` - Zamknij otwarte okna

### API Endpoints:
- `GET /` - Strona główna
- `GET /api/calendar/{year}/{month}` - Dane kalendarza
- `GET /api/events/{date}` - Wydarzenia dla daty
- `POST /api/events` - Dodaj wydarzenie
- `PUT /api/events/{id}` - Edytuj wydarzenie
- `DELETE /api/events/{id}` - Usuń wydarzenie
- `GET /api/search?q={query}` - Wyszukaj wydarzenia

## Autor
Franciszek Łasiński 
