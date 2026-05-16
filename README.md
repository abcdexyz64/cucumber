# Cucumber

Cucumber is an open-source desktop studio for rotoscoped pixel-video art. It converts ordinary video into a consistent retro game look, so AI-generated clips, gameplay references, or filmed motion can land in the same visual language before being used as animation reference, cutscene material, or sprite-sheet source.

## What it does

- Upload MP4, MOV, AVI, MKV, or WEBM video in a local browser UI.
- Preview any frame with the current style settings.
- Apply a stable palette or stable posterization across frames.
- Add rotoscope-style ink outlines with adjustable thresholds and thickness.
- Pixelate the result at a controllable block size.
- Export an MP4 from the processed frames.

## Desktop Quick Start

```powershell
.\launch_desktop.ps1
```

Or run the commands manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python cucumber_desktop.py
```

## Build A Windows App

```powershell
.\build_windows.ps1
```

The executable is created at `dist\Cucumber\Cucumber.exe`.

## Web Prototype

The older Streamlit prototype is still included as a quick browser fallback:

```powershell
.\launch.ps1
```

It opens at `http://localhost:8501`.

## Style Controls

- `Palette`: fixed palettes keep the same colors across batches and reduce visual drift.
- `Pixel size`: larger values make the footage read more like low-resolution game art.
- `Output width`: limits processing cost and sets the exported frame width.
- `Ink strength`: blends detected edges into dark line art.
- `Edge threshold`: controls how aggressively motion and silhouettes are traced.
- `Output FPS`: caps frame rate for a more deliberate animation cadence.
- `Limit frames for test export`: useful while dialing in a style.

## Project layout

```text
assets/                 Cucumber app icon and mascot art
cucumber_desktop.py     PySide6 desktop application
app.py                  Streamlit prototype
rotopixel/processor.py  OpenCV video and image processing core
rotopixel/palettes.py   Fixed game-style palettes
tests/                  Focused processing tests
```

## Notes

This first version is intentionally deterministic. The default palettes and posterization are stable from frame to frame, which helps keep different generated video batches from looking like separate art directions.

## License

MIT
