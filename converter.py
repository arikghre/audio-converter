import shutil
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pydub import AudioSegment


class ConversionEngine:

    def check_ffmpeg(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def convert_file(self, input_path: str, output_path: str, target_format: str) -> tuple[bool, str]:
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=target_format)
            return True, ""
        except Exception as e:
            return False, str(e)


class AppUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Audio Converter — MP3 ↔ WAV")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.root.minsize(600, 400)

        self.engine = ConversionEngine()
        self.files: list[dict] = []
        self.output_dir: str | None = None
        self.direction = tk.StringVar(value="mp3_to_wav")

        self._check_ffmpeg_on_start()
        self._build_ui()

    def _check_ffmpeg_on_start(self):
        if not self.engine.check_ffmpeg():
            messagebox.showwarning(
                "ffmpeg introuvable",
                "ffmpeg n'est pas détecté dans votre PATH.\n\n"
                "Installation Windows :\n"
                "1. Télécharger depuis https://ffmpeg.org/download.html\n"
                "2. Extraire l'archive\n"
                "3. Ajouter le dossier 'bin' au PATH système\n"
                "4. Redémarrer l'application"
            )

    def _build_ui(self):
        # Direction selector
        dir_frame = ttk.LabelFrame(self.root, text="Direction de conversion", padding=8)
        dir_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Radiobutton(dir_frame, text="MP3 → WAV", variable=self.direction,
                        value="mp3_to_wav", command=self._on_direction_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(dir_frame, text="WAV → MP3", variable=self.direction,
                        value="wav_to_mp3", command=self._on_direction_change).pack(side=tk.LEFT, padx=10)

        # Action buttons
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(buttons_frame, text="Ajouter des fichiers",
                   command=self._add_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons_frame, text="Ajouter un dossier",
                   command=self._add_folder).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons_frame, text="Vider la liste",
                   command=self._clear_list).pack(side=tk.LEFT)

        # File list
        list_frame = ttk.LabelFrame(self.root, text="Fichiers", padding=4)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        cols = ("name", "path", "status")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="extended")
        self._tree.heading("name", text="Nom")
        self._tree.heading("path", text="Chemin")
        self._tree.heading("status", text="Statut")
        self._tree.column("name", width=180, anchor=tk.W)
        self._tree.column("path", width=320, anchor=tk.W)
        self._tree.column("status", width=150, anchor=tk.W)

        self._tree.tag_configure("done", foreground="green")
        self._tree.tag_configure("error", foreground="red")
        self._tree.tag_configure("running", foreground="blue")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Output folder
        out_frame = ttk.Frame(self.root)
        out_frame.pack(fill=tk.X, padx=10, pady=(0, 4))

        ttk.Button(out_frame, text="Choisir le dossier de sortie",
                   command=self._choose_output_dir).pack(side=tk.LEFT, padx=(0, 8))
        self._output_label = ttk.Label(out_frame,
                                       text="Dossier de sortie : (même dossier que la source)",
                                       foreground="gray")
        self._output_label.pack(side=tk.LEFT)

        # Progress bar
        self._progress = ttk.Progressbar(self.root, mode="determinate")
        self._progress.pack(fill=tk.X, padx=10, pady=(0, 4))

        # Bottom bar
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._convert_btn = ttk.Button(bottom_frame, text="Convertir",
                                       command=self._start_conversion)
        self._convert_btn.pack(side=tk.RIGHT)

    # --- Direction ---

    def _on_direction_change(self):
        self.files.clear()
        for item in self._tree.get_children():
            self._tree.delete(item)

    def _source_format(self) -> str:
        return "mp3" if self.direction.get() == "mp3_to_wav" else "wav"

    def _target_format(self) -> str:
        return "wav" if self.direction.get() == "mp3_to_wav" else "mp3"

    # --- File management ---

    def _add_files(self):
        fmt = self._source_format()
        paths = filedialog.askopenfilenames(
            title=f"Sélectionner des fichiers {fmt.upper()}",
            filetypes=[(f"Fichiers {fmt.upper()}", f"*.{fmt}"), ("Tous les fichiers", "*.*")]
        )
        self._enqueue_paths(paths)

    def _add_folder(self):
        fmt = self._source_format()
        folder = filedialog.askdirectory(title="Sélectionner un dossier")
        if not folder:
            return
        paths = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(f".{fmt}")
        ]
        if not paths:
            messagebox.showinfo("Aucun fichier", f"Aucun fichier .{fmt} trouvé dans ce dossier.")
            return
        self._enqueue_paths(paths)

    def _enqueue_paths(self, paths):
        existing = {f["path"] for f in self.files}
        for path in paths:
            if path in existing:
                continue
            name = os.path.basename(path)
            entry = {"path": path, "status": "En attente", "tree_id": None}
            tree_id = self._tree.insert("", tk.END, values=(name, path, "En attente"))
            entry["tree_id"] = tree_id
            self.files.append(entry)

    def _clear_list(self):
        self.files.clear()
        for item in self._tree.get_children():
            self._tree.delete(item)
        self.output_dir = None
        self._output_label.config(text="Dossier de sortie : (même dossier que la source)")

    # --- Output folder ---

    def _choose_output_dir(self):
        folder = filedialog.askdirectory(title="Choisir le dossier de sortie")
        if folder:
            self.output_dir = folder
            self._output_label.config(text=f"Dossier de sortie : {folder}")

    def _resolve_output_path(self, input_path: str) -> str:
        base = os.path.splitext(os.path.basename(input_path))[0]
        ext = self._target_format()
        folder = self.output_dir if self.output_dir else os.path.dirname(input_path)
        return os.path.join(folder, f"{base}.{ext}")

    # --- Conversion ---

    def _start_conversion(self):
        if not self.files:
            messagebox.showinfo("Aucun fichier", "Ajoutez des fichiers avant de convertir.")
            return

        if self.output_dir and not os.path.isdir(self.output_dir):
            messagebox.showerror("Dossier invalide",
                                 f"Le dossier de sortie n'existe pas :\n{self.output_dir}")
            return

        self._convert_btn.config(state=tk.DISABLED)
        self._progress["value"] = 0
        self._progress["maximum"] = len(self.files)

        thread = threading.Thread(target=self._run_conversion, daemon=True)
        thread.start()

    def _run_conversion(self):
        for i, entry in enumerate(self.files):
            self.root.after(0, self._set_status, entry, "En cours...")
            output_path = self._resolve_output_path(entry["path"])
            success, error = self.engine.convert_file(entry["path"], output_path, self._target_format())
            if success:
                self.root.after(0, self._set_status, entry, "Terminé ✓")
            else:
                self.root.after(0, self._set_status, entry, f"Erreur ✗ — {error[:60]}")
            self.root.after(0, self._update_progress, i + 1)

        self.root.after(0, self._on_conversion_done)

    def _set_status(self, entry: dict, status: str):
        entry["status"] = status
        name = os.path.basename(entry["path"])
        if status.startswith("Terminé"):
            tag = "done"
        elif status.startswith("Erreur"):
            tag = "error"
        elif status == "En cours...":
            tag = "running"
        else:
            tag = ""
        self._tree.item(entry["tree_id"], values=(name, entry["path"], status), tags=(tag,))

    def _update_progress(self, value: int):
        self._progress["value"] = value

    def _on_conversion_done(self):
        self._convert_btn.config(state=tk.NORMAL)
        done = sum(1 for f in self.files if f["status"] == "Terminé ✓")
        errors = sum(1 for f in self.files if f["status"].startswith("Erreur"))
        messagebox.showinfo("Conversion terminée",
                            f"{done} fichier(s) converti(s) avec succès.\n"
                            f"{errors} erreur(s).")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()
