import shutil
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pydub import AudioSegment


AUDIO_FORMATS = {"mp3", "wav", "flac"}
VIDEO_FORMATS = {"mp4", "avi", "mov"}
IMAGE_FORMATS = {"heic", "jpg", "jpeg", "png"}

COMPATIBLE = {
    "mp3":  ["flac", "wav"],
    "wav":  ["flac", "mp3"],
    "flac": ["mp3", "wav"],
    "mp4":  ["avi", "mov"],
    "avi":  ["mov", "mp4"],
    "mov":  ["avi", "mp4"],
    "heic": ["jpg", "png"],
    "jpg":  ["heic", "png"],
    "png":  ["heic", "jpg"],
}

ALL_FORMATS = sorted(COMPATIBLE.keys())


class ConversionEngine:

    def check_ffmpeg(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def convert_file(self, input_path: str, output_path: str, target_format: str) -> tuple[bool, str]:
        ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        if ext in AUDIO_FORMATS:
            return self._convert_audio(input_path, output_path, target_format)
        elif ext in VIDEO_FORMATS:
            return self._convert_video(input_path, output_path, target_format)
        elif ext in IMAGE_FORMATS:
            return self._convert_image(input_path, output_path, target_format)
        return False, f"Format source non supporté : .{ext}"

    def _convert_audio(self, input_path: str, output_path: str, target_format: str) -> tuple[bool, str]:
        try:
            audio = AudioSegment.from_file(input_path)
            export_kwargs: dict = {"format": target_format}
            if target_format == "mp3":
                export_kwargs["bitrate"] = "320k"
            audio.export(output_path, **export_kwargs)
            return True, ""
        except Exception as e:
            return False, str(e)

    # High-quality ffmpeg flags per output format
    _VIDEO_FLAGS = {
        "mp4": ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a", "320k"],
        "mov": ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a", "320k"],
        "avi": ["-c:v", "mpeg4", "-q:v", "2", "-c:a", "libmp3lame", "-b:a", "320k"],
    }

    def _convert_video(self, input_path: str, output_path: str, target_format: str) -> tuple[bool, str]:
        try:
            flags = self._VIDEO_FLAGS.get(target_format, [])
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", input_path] + flags + [output_path],
                capture_output=True,
                timeout=3600,
            )
            if result.returncode != 0:
                stderr = result.stderr.decode(errors="replace")
                lines = [l for l in stderr.splitlines() if l.strip()]
                return False, lines[-1] if lines else "Erreur ffmpeg inconnue"
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Timeout dépassé (> 1h)"
        except Exception as e:
            return False, str(e)

    def _convert_image(self, input_path: str, output_path: str, target_format: str) -> tuple[bool, str]:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
            from PIL import Image

            img = Image.open(input_path)
            fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "heic": "HEIF"}
            save_format = fmt_map.get(target_format.lower(), target_format.upper())
            if save_format == "JPEG" and img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            save_kwargs: dict = {"format": save_format}
            if save_format == "JPEG":
                save_kwargs["quality"] = 97
                save_kwargs["subsampling"] = 0  # 4:4:4 — aucune perte de chrominance
            elif save_format == "HEIF":
                save_kwargs["quality"] = 95
            img.save(output_path, **save_kwargs)
            return True, ""
        except Exception as e:
            return False, str(e)


class AppUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AG's Media Converter")
        self.root.geometry("760x520")
        self.root.resizable(True, True)
        self.root.minsize(640, 420)

        self.engine = ConversionEngine()
        self.files: list[dict] = []
        self.output_dir: str | None = None

        self.source_fmt = tk.StringVar(value="mp3")
        self.target_fmt = tk.StringVar(value="wav")

        self._check_ffmpeg_on_start()
        self._build_ui()

    def _check_ffmpeg_on_start(self):
        if not self.engine.check_ffmpeg():
            messagebox.showwarning(
                "ffmpeg introuvable",
                "ffmpeg n'est pas détecté dans votre PATH.\n\n"
                "Installation Windows :\n"
                "  winget install --id Gyan.FFmpeg --source winget\n\n"
                "Redémarrez l'application après installation."
            )

    def _build_ui(self):
        # Format selector
        fmt_frame = ttk.LabelFrame(self.root, text="Conversion", padding=10)
        fmt_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Label(fmt_frame, text="Source :").pack(side=tk.LEFT)
        self._src_combo = ttk.Combobox(
            fmt_frame, textvariable=self.source_fmt,
            values=ALL_FORMATS, state="readonly", width=8
        )
        self._src_combo.pack(side=tk.LEFT, padx=(4, 10))
        self._src_combo.bind("<<ComboboxSelected>>", self._on_source_change)

        ttk.Label(fmt_frame, text="→").pack(side=tk.LEFT)

        self._tgt_combo = ttk.Combobox(
            fmt_frame, textvariable=self.target_fmt,
            state="readonly", width=8
        )
        self._tgt_combo.pack(side=tk.LEFT, padx=(10, 0))
        self._refresh_target_formats()

        # Action buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(btn_frame, text="Ajouter des fichiers",
                   command=self._add_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="Ajouter un dossier",
                   command=self._add_folder).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="Vider la liste",
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
        self._tree.column("path", width=330, anchor=tk.W)
        self._tree.column("status", width=160, anchor=tk.W)

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
        self._output_label = ttk.Label(
            out_frame, text="Dossier de sortie : (même dossier que la source)", foreground="gray"
        )
        self._output_label.pack(side=tk.LEFT)

        # Progress bar
        self._progress = ttk.Progressbar(self.root, mode="determinate")
        self._progress.pack(fill=tk.X, padx=10, pady=(0, 4))

        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._convert_btn = ttk.Button(bottom, text="Convertir", command=self._start_conversion)
        self._convert_btn.pack(side=tk.RIGHT)

    # --- Format management ---

    def _refresh_target_formats(self):
        src = self.source_fmt.get()
        targets = COMPATIBLE.get(src, [])
        self._tgt_combo["values"] = targets
        if targets:
            self.target_fmt.set(targets[0])

    def _on_source_change(self, _event=None):
        self._refresh_target_formats()
        self._clear_list()

    def _source_format(self) -> str:
        return self.source_fmt.get()

    def _target_format(self) -> str:
        return self.target_fmt.get()

    # --- File management ---

    def _add_files(self):
        fmt = self._source_format()
        paths = filedialog.askopenfilenames(
            title=f"Sélectionner des fichiers .{fmt.upper()}",
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
        self._src_combo.config(state=tk.DISABLED)
        self._tgt_combo.config(state=tk.DISABLED)
        self._progress["value"] = 0
        self._progress["maximum"] = len(self.files)

        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        target = self._target_format()
        for i, entry in enumerate(self.files):
            self.root.after(0, self._set_status, entry, "En cours...")
            output_path = self._resolve_output_path(entry["path"])
            success, error = self.engine.convert_file(entry["path"], output_path, target)
            status = "Terminé ✓" if success else f"Erreur ✗ — {error[:55]}"
            self.root.after(0, self._set_status, entry, status)
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
        self._src_combo.config(state="readonly")
        self._tgt_combo.config(state="readonly")
        done = sum(1 for f in self.files if f["status"] == "Terminé ✓")
        errors = sum(1 for f in self.files if f["status"].startswith("Erreur"))
        messagebox.showinfo("Conversion terminée",
                            f"{done} fichier(s) converti(s) avec succès.\n{errors} erreur(s).")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()
