"""Tiny Tkinter app: extract a single PNG frame from a video at a timestamp."""

import re
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

OUTPUT_DIR = Path.home() / "Desktop" / "FrameOutput"
TIME_RE = re.compile(r"^\d{1,2}:\d{2}:\d{2}(\.\d{1,3})?$")
VIDEO_EXTS = [("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.m4v"),
              ("All files", "*.*")]
CREATE_NO_WINDOW = 0x08000000  # Windows: suppress console flash from subprocess


def sanitize_timestamp(ts: str) -> str:
    return ts.replace(":", "-").replace(".", "-")


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def extract_frame(video: str, timestamp: str) -> Path:
    video_path = Path(video)
    if not video_path.is_file():
        raise FileNotFoundError(f"Video not found: {video}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = unique_path(
        OUTPUT_DIR / f"{video_path.stem}_{sanitize_timestamp(timestamp)}.png"
    )

    result = subprocess.run(
        ["ffmpeg", "-ss", timestamp, "-i", str(video_path),
         "-frames:v", "1", "-y", str(out)],
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )
    if result.returncode != 0:
        tail = (result.stderr or "").strip().splitlines()[-3:]
        raise RuntimeError(" | ".join(tail) or "ffmpeg failed")
    return out


class App:
    def __init__(self, root: tk.Tk):
        root.title("Frame Extractor")
        root.resizable(False, False)

        frm = ttk.Frame(root, padding=12)
        frm.grid()

        ttk.Label(frm, text="Video:").grid(row=0, column=0, sticky="w", pady=4)
        self.video_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.video_var, width=48).grid(
            row=0, column=1, padx=(6, 6))
        ttk.Button(frm, text="Browse...", command=self.browse).grid(
            row=0, column=2)

        ttk.Label(frm, text="Time:").grid(row=1, column=0, sticky="w", pady=4)
        self.time_var = tk.StringVar(value="00:00:00.000")
        ttk.Entry(frm, textvariable=self.time_var, width=20).grid(
            row=1, column=1, sticky="w", padx=(6, 6))

        ttk.Button(frm, text="Extract frame", command=self.extract).grid(
            row=2, column=0, columnspan=3, pady=(8, 4), sticky="ew")

        self.status = tk.StringVar(value="Ready.")
        self.status_lbl = ttk.Label(
            frm, textvariable=self.status, foreground="gray25",
            wraplength=440, justify="left")
        self.status_lbl.grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 0))

        root.bind("<Control-Return>", lambda _e: self.extract())
        root.bind("<Escape>", lambda _e: root.destroy())

    def browse(self):
        path = filedialog.askopenfilename(filetypes=VIDEO_EXTS)
        if path:
            self.video_var.set(path)

    def set_status(self, msg: str, ok: bool):
        self.status.set(msg)
        self.status_lbl.configure(foreground="#1a7f37" if ok else "#b3261e")

    def extract(self):
        video = self.video_var.get().strip().strip('"')
        timestamp = self.time_var.get().strip()

        if not video:
            self.set_status("Pick a video first.", ok=False)
            return
        if not TIME_RE.match(timestamp):
            self.set_status("Time must look like HH:MM:SS or HH:MM:SS.ms", ok=False)
            return

        try:
            out = extract_frame(video, timestamp)
        except Exception as exc:
            self.set_status(f"Error: {exc}", ok=False)
            return
        self.set_status(f"Saved: {out}", ok=True)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
