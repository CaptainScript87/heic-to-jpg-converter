import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
from PIL import Image

# Import pillow_heif do obsługi formatu HEIC
try:
    import pillow_heif
except ImportError:
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd krytyczny",
                             "Biblioteka pillow-heif nie jest zainstalowana.\n\n"
                             "Aby zainstalować, uruchom w terminalu:\n"
                             "pip install pillow pillow-heif\n\n"
                             "W systemach Linux może być wymagane:\n"
                             "sudo apt-get update && sudo apt-get install libheif-dev")
    except tk.TclError:
        print("Błąd: Biblioteka pillow-heif nie jest zainstalowana.")
        print("Aby zainstalować, uruchom: pip install pillow pillow-heif")
        print("W systemach Linux może być wymagane zainstalowanie libheif-dev:")
        print("sudo apt-get update && sudo apt-get install libheif-dev")
    sys.exit(1)

pillow_heif.register_heif_opener()

# --- Logika konwersji ---

def convert_heic_to_jpg(heic_path, jpg_path, log_func, quality=95):
    """
    Konwertuje pojedynczy plik HEIC do formatu JPG i loguje postęp.
    Zwraca True w przypadku sukcesu, False w przypadku błędu.
    """
    try:
        # Utwórz folder docelowy, jeśli nie istnieje (ważne dla konwersji pojedynczego pliku)
        output_dir = os.path.dirname(jpg_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                log_func(f"Utworzono folder docelowy: {output_dir}")
            except OSError as e:
                log_func(f"Błąd: Nie można utworzyć folderu docelowego '{output_dir}': {e}")
                return False

        image = Image.open(heic_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(jpg_path, format='JPEG', quality=quality)
        log_func(f"OK (jakość {quality}): {os.path.basename(heic_path)} -> {os.path.basename(jpg_path)}")
        return True
    except FileNotFoundError:
        log_func(f"Błąd: Plik wejściowy nie znaleziony: {heic_path}")
        return False
    except Exception as e:
        log_func(f"Błąd konwersji {os.path.basename(heic_path)}: {e}")
        return False

# --- Wątki konwersji ---

def batch_convert_thread(input_dir, output_dir, log_func, progress_callback, quality):
    """
    Funkcja konwersji wsadowej (folder) przeznaczona do uruchomienia w osobnym wątku.
    """
    if not os.path.isdir(input_dir):
        log_func(f"Błąd: Folder wejściowy '{input_dir}' nie istnieje.")
        progress_callback(0, 0, 0, True)
        return

    # Sprawdzenie folderu wyjściowego jest teraz w convert_heic_to_jpg,
    # ale możemy zostawić tu logowanie o rozpoczęciu.
    log_func(f"Rozpoczynanie konwersji folderu '{input_dir}' do '{output_dir}' (jakość: {quality})...")

    files_to_convert = [f for f in os.listdir(input_dir) if f.lower().endswith(".heic")]
    converted_count = 0
    skipped_count = 0
    error_count = 0

    for filename in files_to_convert:
        heic_file_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        # Ścieżka wyjściowa jest konstruowana dla każdego pliku
        jpg_file_path = os.path.join(output_dir, f"{base_name}.jpg")

        # Sprawdzenie istnienia pliku wyjściowego
        if os.path.exists(jpg_file_path):
            log_func(f"Pominięto (istnieje): {os.path.basename(jpg_file_path)}")
            skipped_count += 1
        elif os.path.isfile(heic_file_path):
            # Funkcja convert_heic_to_jpg sama sprawdzi/utworzy folder docelowy
            if convert_heic_to_jpg(heic_file_path, jpg_file_path, log_func, quality):
                 converted_count += 1
            else:
                 error_count += 1
        else:
             log_func(f"Pominięto (nie plik): {filename}")
             skipped_count += 1

    log_func("\nKonwersja folderu zakończona.")
    log_func(f"Przekonwertowano: {converted_count}")
    log_func(f"Pominięto: {skipped_count}")
    log_func(f"Błędy: {error_count}")
    progress_callback(converted_count, skipped_count, error_count, False)


def single_convert_thread(input_path, output_path, log_func, quality, callback_func):
    """
    Funkcja konwersji pojedynczego pliku przeznaczona do uruchomienia w osobnym wątku.
    """
    log_func(f"Rozpoczynanie konwersji pliku '{os.path.basename(input_path)}' do '{os.path.basename(output_path)}' (jakość: {quality})...")
    # Funkcja convert_heic_to_jpg sama sprawdzi/utworzy folder docelowy
    success = convert_heic_to_jpg(input_path, output_path, log_func, quality)
    if success:
        log_func("Konwersja pliku zakończona pomyślnie.")
    else:
        log_func("Konwersja pliku nie powiodła się.")
    callback_func(success)


# --- GUI ---

class HeicConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Konwerter HEIC do JPG")
        master.geometry("600x530")

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.quality_var = tk.IntVar(value=95)

        # --- Ramka dla wyboru folderów ---
        folder_frame = tk.LabelFrame(master, text="Konwersja folderu", padx=10, pady=10)
        folder_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(folder_frame, text="Folder z plikami HEIC:").grid(row=0, column=0, sticky=tk.W, pady=2)
        input_entry = tk.Entry(folder_frame, textvariable=self.input_dir, width=50)
        input_entry.grid(row=0, column=1, padx=5, pady=2)
        input_button = tk.Button(folder_frame, text="Przeglądaj...", command=self.select_input_dir)
        input_button.grid(row=0, column=2, padx=5, pady=2)

        tk.Label(folder_frame, text="Folder docelowy (JPG):").grid(row=1, column=0, sticky=tk.W, pady=2)
        output_entry = tk.Entry(folder_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, padx=5, pady=2)
        output_button = tk.Button(folder_frame, text="Przeglądaj...", command=self.select_output_dir)
        output_button.grid(row=1, column=2, padx=5, pady=2)

        self.convert_folder_button = tk.Button(folder_frame, text="Konwertuj cały folder", command=self.start_batch_conversion, font=('Helvetica', 10, 'bold'))
        self.convert_folder_button.grid(row=2, column=0, columnspan=3, pady=(10, 5))


        # --- Ramka dla ustawień jakości ---
        quality_frame = tk.Frame(master, padx=10, pady=5)
        quality_frame.pack(fill=tk.X, padx=10)

        tk.Label(quality_frame, text="Jakość JPG (1-100):").pack(side=tk.LEFT, padx=5)
        self.quality_label = tk.Label(quality_frame, textvariable=self.quality_var, width=3)
        self.quality_label.pack(side=tk.RIGHT, padx=5)
        quality_scale = ttk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, command=self._update_quality_label)
        quality_scale.set(95)
        quality_scale.pack(fill=tk.X, expand=True, side=tk.RIGHT, padx=5)

        # --- Ramka dla konwersji pojedynczego pliku ---
        single_file_frame = tk.LabelFrame(master, text="Konwersja pojedynczego pliku", padx=10, pady=10)
        single_file_frame.pack(fill=tk.X, padx=10, pady=5)

        # Zmieniono tekst przycisku, aby było jasne, że zapisze do folderu docelowego
        self.convert_single_button = tk.Button(single_file_frame, text="Wybierz plik HEIC i konwertuj (do folderu docelowego)", command=self.select_and_convert_single_file, font=('Helvetica', 10, 'bold'))
        self.convert_single_button.pack(pady=5)


        # --- Ramka dla statusu i logów ---
        status_log_frame = tk.Frame(master, padx=10, pady=5)
        status_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.status_label = tk.Label(status_log_frame, text="Wybierz opcję konwersji", fg="blue")
        self.status_label.pack(pady=2)

        tk.Label(status_log_frame, text="Log konwersji:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(status_log_frame, wrap=tk.WORD, height=10, width=70, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)


    def _update_quality_label(self, value):
        self.quality_var.set(int(float(value)))

    def select_input_dir(self):
        dir_path = filedialog.askdirectory(title="Wybierz folder z plikami HEIC")
        if dir_path:
            self.input_dir.set(dir_path)
            self.update_status("Gotowy do konwersji folderu.")

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="Wybierz folder docelowy dla plików JPG")
        if dir_path:
            self.output_dir.set(dir_path)
            # Aktualizuj status, wskazując gotowość do obu typów konwersji
            self.update_status("Wybrano folder docelowy. Gotowy do konwersji.")

    def log_message(self, message):
        self.master.after(0, self._append_log, message)

    def _append_log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def update_status(self, message, color="blue"):
        self.status_label.config(text=message, fg=color)

    def set_buttons_state(self, state):
        self.convert_folder_button.config(state=state)
        self.convert_single_button.config(state=state)

    # --- Logika startu konwersji ---

    def start_batch_conversion(self):
        input_p = self.input_dir.get()
        output_p = self.output_dir.get()
        quality_val = self.quality_var.get()

        if not input_p or not output_p:
            messagebox.showwarning("Brak folderów", "Proszę wybrać folder wejściowy i wyjściowy dla konwersji folderu.")
            return
        if not os.path.isdir(input_p):
             messagebox.showerror("Błąd", f"Folder wejściowy nie istnieje:\n{input_p}")
             return
        # Sprawdzenie folderu wyjściowego przeniesione do funkcji konwertującej

        self._clear_logs()
        self.update_status(f"Konwersja folderu w toku (jakość: {quality_val})...", "orange")
        self.set_buttons_state(tk.DISABLED)

        conversion_thread = threading.Thread(
            target=batch_convert_thread,
            args=(input_p, output_p, self.log_message, self.batch_conversion_finished, quality_val),
            daemon=True
        )
        conversion_thread.start()

    def select_and_convert_single_file(self):
        """Wybiera plik wejściowy i konwertuje go do ustalonego folderu wyjściowego."""
        # Najpierw sprawdź, czy folder wyjściowy jest ustawiony
        output_p = self.output_dir.get()
        if not output_p:
            messagebox.showwarning("Brak folderu docelowego", "Proszę najpierw wybrać 'Folder docelowy (JPG)' w sekcji konwersji folderu.")
            return

        input_path = filedialog.askopenfilename(
            title="Wybierz plik HEIC do konwersji",
            filetypes=[("HEIC files", "*.heic"), ("All files", "*.*")]
        )
        if not input_path:
            return # Użytkownik anulował

        # Skonstruuj ścieżkę wyjściową na podstawie folderu docelowego i nazwy pliku wejściowego
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_p, f"{base_name}.jpg")

        # Sprawdź, czy plik wyjściowy już istnieje
        if os.path.exists(output_path):
             if not messagebox.askyesno("Plik istnieje", f"Plik '{os.path.basename(output_path)}' już istnieje w folderze docelowym.\nCzy chcesz go nadpisać?"):
                 self.log_message(f"Pominięto (anulowano nadpisanie): {os.path.basename(output_path)}")
                 return # Użytkownik nie chce nadpisywać

        quality_val = self.quality_var.get()

        self._clear_logs()
        self.update_status(f"Konwersja pliku w toku (jakość: {quality_val})...", "orange")
        self.set_buttons_state(tk.DISABLED)

        conversion_thread = threading.Thread(
            target=single_convert_thread,
            args=(input_path, output_path, self.log_message, quality_val, self.single_conversion_finished),
            daemon=True
        )
        conversion_thread.start()

    def _clear_logs(self):
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')

    # --- Funkcje zwrotne (callback) po zakończeniu konwersji ---

    def batch_conversion_finished(self, converted, skipped, errors, critical_error):
        if critical_error:
            self.update_status("Konwersja folderu zakończona z błędem krytycznym.", "red")
            messagebox.showerror("Błąd", "Wystąpił błąd krytyczny podczas konwersji folderu. Sprawdź logi.")
        elif errors > 0:
             self.update_status(f"Konwersja folderu zakończona (OK: {converted}, Pominięto: {skipped}, Błędy: {errors}).", "orange")
             messagebox.showinfo("Zakończono z problemami", f"Konwersja folderu zakończona.\nPrzekonwertowano: {converted}\nPominięto: {skipped}\nBłędy: {errors}")
        else:
            self.update_status(f"Konwersja folderu zakończona pomyślnie (OK: {converted}, Pominięto: {skipped}).", "green")
            messagebox.showinfo("Zakończono", f"Konwersja folderu zakończona pomyślnie!\nPrzekonwertowano: {converted}\nPominięto: {skipped}")

        self.set_buttons_state(tk.NORMAL)

    def single_conversion_finished(self, success):
        if success:
            self.update_status("Konwersja pliku zakończona pomyślnie.", "green")
            messagebox.showinfo("Zakończono", "Plik został pomyślnie przekonwertowany.")
        else:
            self.update_status("Konwersja pliku nie powiodła się.", "red")
            messagebox.showerror("Błąd", "Nie udało się przekonwertować pliku. Sprawdź logi.")

        self.set_buttons_state(tk.NORMAL)


# --- Główna część skryptu ---
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass
    app = HeicConverterApp(root)
    root.mainloop()
