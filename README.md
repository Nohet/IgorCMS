## Co to jest?
IgorCMS to CMS(System Zarządzania Treścią) napisany w pythonie używając
framework'a Starlette i bazy danych MySQL/MariaDB.

Kod nie jest najlepiej napisany, ale będzie sumiennie poprawiany.

---

## Screenshot
![Screenshot przedstawiający panel administracyjny](https://i.imgur.com/wHLl7FK.png)

---


## Jak uruchomić mojego CMS-a?
Zalecana wersja Pythona: <3.10

1. Zainstalować wymagane biblioteki:
    - `pip install -r requirements.txt`

2. Uruchomić bazę danych (MySQL/MariaDB).

3. Stworzyć pustą bazę danych, która zostanie wykorzystana przez CMS-a.
   Jej nazwę należy podać podczas pierwszej konfiguracji.

4. Włączyć CMS-a. CMS domyślnie działa w trybie debugowania. Aby go wyłączyć, zmień wartość `debug=True` na `debug=False` w pliku `app.py`:
    - `uvicorn app:app` lub `python -m uvicorn app:app`

5. Otworzyć przeglądarkę i przejść na stronę CMS-a.
   Jeśli CMS nie jest skonfigurowany, pojawi się formularz umożliwiający przeprowadzenie konfiguracji i utworzenie pierwszego konta.

---

## Funkcje mojego CMS-a:
- Tworzenie, edytowanie, usuwanie stron.
- Tworzenie, edytowanie, usuwanie kategorii.
- Tworzenie, edytowanie, usuwanie postów.
- Dodawanie komentarzy do postów.
- Edytor WYSIWYG (What You See Is What You Get):
  - Obsługa formatowania tekstu (nagłówki, listy, cytaty itp.).
  - Możliwość podglądu wersji roboczej przed publikacją.
- Rejestracja i logowanie użytkowników.
- System ról i uprawnień (np. autor, administrator).
- Zmienianie haseł.
- Przechowywanie i organizowanie plików (obrazy, wideo, dokumenty).
- Zarządzanie meta tagami (tytuł, opis, słowa kluczowe).
- Przyjazne dla wyszukiwarek adresy URL (SEO-friendly URLs).
- Automatyczne generowanie mapy strony (`sitemap.xml`).
- Bezpieczeństwo:
  - Autoryzacja przez JWT.
  - Ochrona przed atakami XSS i CSRF.
  - Hashowanie haseł użytkowników (bcrypt).
- Obsługa wtyczek.
- API umożliwiające korzystanie z CMS-a w trybie headless (bez panelu graficznego).
- Asynchroniczna obsługa zapytań.

---
