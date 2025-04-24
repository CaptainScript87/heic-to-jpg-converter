Konwerter HEIC do JPG
Prosty program w Pythonie z interfejsem graficznym (GUI) do konwersji zdjęć w formacie HEIC (często używanym przez urządzenia Apple) do bardziej popularnego formatu JPG.

Funkcje
Konwersja wsadowa: Konwertuje wszystkie pliki .heic z wybranego folderu do formatu .jpg w innym wskazanym folderze.

Konwersja pojedynczego pliku: Umożliwia wybór jednego pliku .heic i zapisanie go jako .jpg w folderze docelowym.

Kontrola jakości: Suwak pozwala na ustawienie jakości kompresji JPG (1-100, domyślnie 95).

Prosty interfejs graficzny: Łatwy w obsłudze interfejs zbudowany przy użyciu tkinter.

Logowanie: Wyświetla postęp i ewentualne błędy w oknie logów.

Wymagania
Python 3.x

Biblioteki Python (zainstaluj za pomocą pip):

pillow

pillow-heif

Instalacja zależności
Upewnij się, że masz zainstalowany Python i pip.

Otwórz terminal lub wiersz polecenia i uruchom:

pip install pillow pillow-heif

Uwaga dla użytkowników Linux: Może być konieczne zainstalowanie dodatkowej zależności systemowej przed pillow-heif:

sudo apt-get update && sudo apt-get install libheif-dev
# lub odpowiednik dla Twojej dystrybucji

Użycie
Pobierz plik skryptu konwerter.py.

Uruchom skrypt z poziomu terminala:

python konwerter.py

W oknie aplikacji:

W sekcji "Konwersja folderu" wybierz folder źródłowy (z plikami HEIC) i folder docelowy (gdzie mają być zapisane pliki JPG).

Ustaw żądaną jakość JPG za pomocą suwaka.

Kliknij "Konwertuj cały folder", aby przetworzyć wszystkie pliki .heic z folderu źródłowego.

LUB w sekcji "Konwersja pojedynczego pliku" kliknij "Wybierz plik HEIC i konwertuj...", aby wybrać jeden plik i zapisać go w folderze docelowym.

Obserwuj postęp w oknie logów.

(Opcjonalnie) Tworzenie pliku .exe
Możesz stworzyć samodzielny plik wykonywalny .exe (dla systemu Windows) za pomocą PyInstaller:

Zainstaluj PyInstaller: pip install pyinstaller

Przejdź do folderu ze skryptem w terminalu.

Uruchom (zalecana metoda):

python -m PyInstaller --onefile --windowed konwerter.py

Gotowy plik .exe znajdziesz w folderze dist.

Licencja
Ten projekt jest udostępniany na licencji MIT - zobacz plik LICENSE (jeśli go dodasz) lub odwiedź https://opensource.org/licenses/MIT po szczegóły.