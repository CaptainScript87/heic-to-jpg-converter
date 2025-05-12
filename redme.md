# Konwerter HEIC do JPG

Program w Pythonie z GUI do konwersji zdjęć HEIC (popularnych na urządzeniach Apple) do formatu JPG.

## Funkcje

* **Konwersja folderu:** Przetwarza wszystkie pliki `.heic` ze wskazanego folderu do folderu docelowego.
* **Konwersja pliku:** Konwertuje pojedynczy plik `.heic` do folderu docelowego.
* **Kontrola jakości:** Suwak do ustawienia jakości JPG (1-100).
* **GUI:** Prosty interfejs graficzny (`tkinter`).
* **Logowanie:** Wyświetla postęp i błędy.

## Wymagania

* Python 3.x
* Biblioteki: `pillow`, `pillow-heif` (zainstaluj przez pip)

## Instalacja zależności

1.  Upewnij się, że masz Python i pip.
2.  W terminalu uruchom:
    ```bash
    pip install pillow pillow-heif
    ```
3.  *Linux:* Może być potrzebne `sudo apt-get update && sudo apt-get install libheif-dev` (lub odpowiednik).

## Użycie

1.  Pobierz `konwerter.py`.
2.  Uruchom: `python konwerter.py`
3.  W aplikacji:
    * Wybierz folder źródłowy i docelowy (dla konwersji folderu).
    * Ustaw jakość suwakiem.
    * Kliknij "Konwertuj cały folder" lub "Wybierz plik HEIC i konwertuj..." (zapisze do folderu docelowego).
    * Śledź postęp w logach.

## (Opcjonalnie) Tworzenie pliku .exe (Windows)

1.  Zainstaluj PyInstaller: `pip install pyinstaller`
2.  W terminalu, w folderze ze skryptem, uruchom:
    ```bash
    python -m PyInstaller --onefile --windowed konwerter.py
    ```
3.  Plik `.exe` znajdziesz w folderze `dist`.

## Licencja

Projekt udostępniany na licencji MIT. Szczegóły: <https://opensource.org/licenses/MIT>