# PathoLens WSI Viewer

This repository contains a simple Flask application for viewing Whole-Slide Images (WSI) with optional heatmap overlays.

## Usage

1. Install dependencies:
   ```bash
   pip install -r wsi_viewer/requirements.txt
   ```
2. Place your slides in `wsi_viewer/wsi_viewer_app/slides/` and heatmaps in `wsi_viewer/wsi_viewer_app/heatmaps/`.
3. Specify default filenames via environment variables (optional):
   ```bash
   export DEFAULT_SLIDE=my_slide.svs
   export DEFAULT_HEATMAP=my_heatmap.png
   ```
4. Run the viewer:
   ```bash
   python wsi_viewer/wsi_viewer_app/app.py
   ```
5. Open your browser at [http://localhost:5000](http://localhost:5000). You can override the defaults using query parameters:
   `http://localhost:5000/?slide=another_slide.svs&heatmap=another_heatmap.png`.
