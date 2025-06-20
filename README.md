# PathoLens WSI Viewer

This repository provides a lightweight web-based whole-slide image (WSI) viewer with an optional heatmap overlay. It is intended for quickly visualizing pathology slides and heatmaps generated from other models or tools.

## Installation

Install the required Python packages using `pip`:

```bash
pip install -r wsi_viewer/requirements.txt
```

## Usage

1. Place your slide files (e.g. `.svs` or `.tiff`) inside a `slides/` directory at the repository root. The application will create this directory automatically if it does not exist.
2. Place heatmap images (e.g. `.png`) inside a `heatmaps/` directory at the repository root.
3. Run the viewer:

```bash
python wsi_viewer/wsi_viewer_app/app.py
```

The server starts on `http://localhost:5000` and serves a simple OpenSeadragon viewer. Edit `wsi_viewer/wsi_viewer_app/app.py` to specify the slide and heatmap filenames to load.

## Reference Materials

Two text files—`Adk-documentation-short.txt` and `Trident Tool kit .txt`—are provided for reference only. They contain documentation for the Agent Development Kit (ADK) and Trident tool kit.
