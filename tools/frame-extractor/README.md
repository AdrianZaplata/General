# Frame Extractor

Tiny Tkinter GUI that grabs a single PNG frame from a video at a timestamp
you specify. It's a thin wrapper around:

```
ffmpeg -ss <time> -i <video> -frames:v 1 -y <output>
```

## Prerequisites

- **Python 3** on PATH (Tkinter ships with the standard installer on Windows
  and macOS; on Linux install `python3-tk`).
- **ffmpeg** on PATH. On Windows: `winget install Gyan.FFmpeg`. On macOS:
  `brew install ffmpeg`. On Linux: your distro's package manager.

## Run it

- **Windows:** double-click `run.bat` (uses `pythonw`, no console window).
- **Any OS:** `python tools/frame-extractor/extract.py` from the repo root.

## Use it

1. Click **Browse...** and pick a video (`.mp4 .mkv .mov .avi .webm .m4v`).
2. Enter a timestamp as `HH:MM:SS` or `HH:MM:SS.ms` (e.g. `00:01:23.500`).
3. Click **Extract frame** (or press `Ctrl+Enter`). `Esc` closes the window.

PNGs are saved to `~/Desktop/FrameOutput` (created on first run). Filenames
look like `<videostem>_<HH-MM-SS-ms>.png`, with `_1`, `_2`, ... suffixes
appended if the same frame is extracted twice — nothing is overwritten.
