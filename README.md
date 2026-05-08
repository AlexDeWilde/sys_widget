# System Stats Desktop Widget

## Overview

A lightweight, frameless, and always-on-top desktop widget written in Python (Tkinter). It asynchronously polls and displays system hardware performance and the local status of Ollama, designed to have practically zero impact on system performance.

## File Structure

- `app.py`: The main Tkinter application script handling the UI and fetching logic.
- `Launch.bat`: A simple batch file utilizing `pythonw` to safely launch the widget in the background without any lingering black console windows.

## Data Sources & Dependencies

This widget relies on built-in OS tools and simple Python libraries:

- **GPU 3D Load, Temperature, & VRAM:** Fetched using `nvidia-smi` via a subprocess command. By leveraging the built-in NVIDIA toolkit, we avoid installing heavy third-party graphics libraries.
- **RAM Usage:** Fetched using the standard `psutil.virtual_memory().percent` function.
- **Ollama Status:** Fetched by silently hitting Ollama's local process API (`http://127.0.0.1:11434/api/ps`). If it connects, it grabs the active model name; otherwise, it reports as `OFF`.

## Technical & Design Decisions

- **Threading:** Hardware polling is spun up on a background daemon thread (`threading.Thread`) every 1 second. This ensures that the HTTP request timeout or subprocess call never freezes or stutters the GUI window.
- **Formatting:** Data is strictly string-formatted to maintain 2 digits (e.g., `05%`, `08C`) so width stays somewhat consistent.
- **Styling:** Bright blue (`#00BFFF`) Consolas font on a black background.

## For Future Assistants / Development

If you are an AI reading this to help the user modify the widget:

1. All logic is contained in `app.py`.
2. Do not introduce synchronous blocking code to the Tkinter `mainloop`.
3. If expanding NVIDIA metrics, utilize the existing `--query-gpu` comma-separated list format in the `subprocess` call rather than adding new external packages.
4. If testing modifications, close the current instance via right-click before attempting to restart it to avoid overlapping windows.
