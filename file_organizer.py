from pathlib import Path
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv"],
    "Archives": [".zip", ".rar", ".7z"],
    "Media": [".mp4", ".mp3", ".wav", ".mkv"],
    "Code": [".py", ".js", ".html", ".css", ".java"]
}

BG = "#fff5f7"
CARD = "#ffffff"
CARD_ALT = "#ffe9ee"
BORDER = "#fbaaba"
TEXT = "#3d1f2e"
MUTED = "#8a6472"
ACCENT_DK = "#db2777"
GOLD = "#9d174d"
SUCCESS = "#059669"
DANGER = "#e11d48"


def get_category(file_path):
    for category, extensions in CATEGORIES.items():
        if file_path.suffix.lower() in extensions:
            return category
    return "Others"


def get_safe_destination(destination):
    if not destination.exists():
        return destination
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return destination.with_name(
        "{}_{}{}".format(destination.stem, timestamp, destination.suffix)
    )


def make_button(parent, text, command, bg, hover_bg, fg="#ffffff"):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        activebackground=hover_bg, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        padx=20, pady=10
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


class FileOrganizer:
    def __init__(self, root):
        self.root = root
        root.title("File Organizer")
        root.geometry("900x680")
        root.configure(bg=BG)
        self.source_folder = tk.StringVar()
        self.build()

    def build(self):
        # Header
        tk.Label(self.root, text="File Organizer", bg=BG, fg=GOLD,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w",
                                                     padx=32, pady=(24, 4))
        tk.Label(self.root,
                 text="Sort files into clean category folders.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w",
                                                              padx=32)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x",
                                                      padx=32, pady=16)

        # Source folder card
        card = tk.Frame(self.root, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=32)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=16, pady=14)

        tk.Label(inner, text="SOURCE FOLDER", bg=CARD, fg=ACCENT_DK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        row = tk.Frame(inner, bg=CARD)
        row.pack(fill="x", pady=(8, 0))

        tk.Entry(row, textvariable=self.source_folder, bg=CARD_ALT,
                 fg=TEXT, relief="flat", font=("Segoe UI", 10),
                 highlightthickness=1, highlightbackground=BORDER).pack(
            side="left", fill="x", expand=True, ipady=9, padx=(0, 10))

        make_button(row, "Browse...", self.select_folder,
                    "#fb7185", "#e11d48").pack(side="left")

        # Action buttons
        actions = tk.Frame(self.root, bg=BG)
        actions.pack(fill="x", padx=32, pady=16)

        make_button(actions, "Preview Files", self.preview_files,
                    "#a78bfa", "#8b5cf6").pack(side="left", padx=(0, 10))
        make_button(actions, "Organize Files", self.organize_files,
                    "#10b981", "#059669").pack(side="left", padx=(0, 10))
        make_button(actions, "Clear Log", self.clear_results,
                    "#94a3b8", "#64748b").pack(side="left")

        # Log
        tk.Label(self.root, text="ACTIVITY LOG", bg=BG, fg=ACCENT_DK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=32)
        log_frame = tk.Frame(self.root, bg=CARD,
                             highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=32, pady=(6, 18))

        self.results = tk.Text(log_frame, wrap="word",
                               font=("Consolas", 10), bg=CARD, fg=TEXT,
                               relief="flat", bd=0, padx=16, pady=14)
        self.results.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(log_frame, orient="vertical",
                           command=self.results.yview)
        sb.pack(side="right", fill="y")
        self.results.configure(yscrollcommand=sb.set)

        self.results.tag_config("header", foreground=GOLD)
        self.results.tag_config("muted", foreground=MUTED)
        self.results.tag_config("success", foreground=SUCCESS)
        self.results.tag_config("error", foreground=DANGER)
        self.results.tag_config("accent", foreground="#8b5cf6")

        self.log("Welcome! Select a folder, then click Preview Files.", "muted")

    def log(self, msg="", tag=None):
        self.results.insert("end", msg + "\n", tag or ())
        self.results.see("end")

    def clear_results(self):
        self.results.delete("1.0", "end")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)
            self.clear_results()
            self.log("Selected: " + folder, "accent")
            self.log("Click Preview Files.", "muted")

    def get_files(self):
        text = self.source_folder.get().strip().strip('"')
        if not text:
            messagebox.showwarning("Oops", "Select a folder first.")
            return None, None
        source = Path(text).resolve()
        if not source.is_dir():
            messagebox.showerror("Error", "Folder does not exist.")
            return None, None
        names = list(CATEGORIES.keys()) + ["Others"]
        paths = {(source / n).resolve() for n in names}
        files = [f for f in source.iterdir()
                 if f.is_file() and f.resolve() not in paths]
        return source, files

    def preview_files(self):
        source, files = self.get_files()
        if source is None:
            return
        self.clear_results()
        self.log("PREVIEW", "header")
        self.log("-" * 50, "muted")
        if not files:
            self.log("No files found.", "muted")
            return
        for f in files:
            cat = get_category(f)
            dest = source / cat / f.name
            if dest.exists():
                dest = get_safe_destination(dest)
            self.log("  " + f.name, "muted")
            self.log("    -> " + cat + "/" + dest.name, "accent")
        self.log("")
        self.log("Ready: " + str(len(files)) + " file(s). No files moved.",
                 "success")

    def organize_files(self):
        source, files = self.get_files()
        if source is None:
            return
        if not files:
            self.log("No files found.", "muted")
            return
        if not messagebox.askyesno("Confirm",
                                   "Move " + str(len(files)) + " file(s)?"):
            return
        self.clear_results()
        self.log("ORGANIZING", "header")
        moved = failed = 0
        for f in files:
            try:
                cat = get_category(f)
                folder = source / cat
                folder.mkdir(exist_ok=True)
                dest = get_safe_destination(folder / f.name)
                shutil.move(str(f), str(dest))
                self.log("  [OK] " + f.name, "success")
                moved += 1
            except Exception as e:
                self.log("  [X] " + f.name + " - " + str(e), "error")
                failed += 1
        self.log("")
        self.log("Done. Moved: " + str(moved) + " Failed: " + str(failed),
                 "success" if not failed else "error")
        messagebox.showinfo("Done", "Moved: " + str(moved) +
                            "\nFailed: " + str(failed))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizer(root)
    root.mainloop()