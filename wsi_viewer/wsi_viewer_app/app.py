import os
from flask import Flask, render_template, send_file, abort, make_response, request
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
from PIL import Image
import io

# Initialize Flask app
app = Flask(__name__)

# Configuration
SLIDE_DIR = 'slides'
HEATMAP_DIR = 'heatmaps'
DEFAULT_SLIDE = os.environ.get('DEFAULT_SLIDE', 'placeholder.svs')
DEFAULT_HEATMAP = os.environ.get('DEFAULT_HEATMAP', 'placeholder_heatmap.png')
TILE_SIZE = 254  # Tile size for Deep Zoom
OVERLAP = 1      # Overlap for Deep Zoom tiles
JPEG_QUALITY = 80 # Quality for JPEG tiles

# --- Helper Functions ---
def get_slide_path(slide_filename):
    """Constructs the full path to a slide file."""
    return os.path.join(SLIDE_DIR, slide_filename)

def get_heatmap_path(heatmap_filename):
    """Constructs the full path to a heatmap file."""
    return os.path.join(HEATMAP_DIR, heatmap_filename)

# In-memory cache for OpenSlide and DeepZoomGenerator objects
# This is a simple cache; for production, consider a more robust solution (e.g., Redis, Memcached)
slide_cache = {}

def get_slide_and_dz(slide_filename):
    """
    Retrieves or loads an OpenSlide object and its DeepZoomGenerator.
    Uses a simple in-memory cache.
    """
    if slide_filename not in slide_cache:
        slide_path = get_slide_path(slide_filename)
        if not os.path.exists(slide_path):
            return None, None
        try:
            slide = OpenSlide(slide_path)
            dz = DeepZoomGenerator(slide, tile_size=TILE_SIZE, overlap=OVERLAP, limit_bounds=False)
            slide_cache[slide_filename] = (slide, dz)
        except OpenSlideError as e:
            print(f"Error opening slide {slide_filename}: {e}")
            return None, None
    return slide_cache[slide_filename]

# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    slide_filename = request.args.get('slide') or DEFAULT_SLIDE
    heatmap_filename = request.args.get('heatmap') or DEFAULT_HEATMAP
    
    slide_path = get_slide_path(slide_filename)
    heatmap_path = get_heatmap_path(heatmap_filename)

    if not os.path.exists(slide_path):
        return (
            "Error: Slide file not found. Provide ?slide=<filename> or set DEFAULT_SLIDE.",
            404,
        )
    if not os.path.exists(heatmap_path):
        return (
            "Error: Heatmap file not found. Provide ?heatmap=<filename> or set DEFAULT_HEATMAP.",
            404,
        )
        
    return render_template('index.html', slide_filename=slide_filename, heatmap_filename=heatmap_filename)

@app.route('/slides/<slide_filename>.dzi')
def dzi_metadata(slide_filename):
    """
    Serves the DZI metadata file for a slide.
    OpenSeadragon uses this to understand the slide's structure.
    """
    slide, dz = get_slide_and_dz(slide_filename)
    if slide is None or dz is None:
        abort(404, description="Slide not found or could not be opened.")
    
    response = make_response(dz.get_dzi('jpeg')) # Using 'jpeg' for tiles
    response.mimetype = 'application/xml'
    return response

@app.route('/slides/<slide_filename>_files/<int:level>/<int:col>_<int:row>.<image_format>')
def dzi_tile(slide_filename, level, col, row, image_format):
    """
    Serves a specific tile from the Deep Zoom Image.
    """
    slide, dz = get_slide_and_dz(slide_filename)
    if slide is None or dz is None:
        abort(404, description="Slide not found or could not be opened.")

    if image_format not in ['jpeg', 'png']:
        abort(404, description="Format not supported.")

    try:
        tile = dz.get_tile(level, (col, row))
    except ValueError as e: # Can happen if tile coordinates are out of bounds for a level
        print(f"Error getting tile for {slide_filename} at level {level}, col {col}, row {row}: {e}")
        # Return a blank tile or a specific error image if preferred
        # For simplicity, aborting here.
        abort(404, description=f"Invalid tile coordinates: {e}")
    except Exception as e:
        print(f"Unexpected error getting tile: {e}")
        abort(500, description="Error generating tile.")
        
    if tile is None:
        abort(404, description="Tile not found (possibly out of bounds).")

    # Convert PIL Image to bytes
    buf = io.BytesIO()
    if image_format == 'jpeg':
        tile.save(buf, 'jpeg', quality=JPEG_QUALITY)
        mimetype = 'image/jpeg'
    elif image_format == 'png': # PNG can be slower but might be needed for transparency
        tile.save(buf, 'png')
        mimetype = 'image/png'
    
    buf.seek(0)
    response = make_response(send_file(buf, mimetype=mimetype))
    return response

@app.route('/heatmaps/<heatmap_filename>')
def serve_heatmap(heatmap_filename):
    """Serves the heatmap image."""
    heatmap_path = get_heatmap_path(heatmap_filename)
    if not os.path.exists(heatmap_path):
        abort(404, description="Heatmap not found.")
    return send_file(heatmap_path)

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(SLIDE_DIR, exist_ok=True)
    os.makedirs(HEATMAP_DIR, exist_ok=True)
    
    # Reminder to add placeholder files if they don't exist
    if not os.path.exists(get_slide_path(DEFAULT_SLIDE)):
        print(
            f"Warning: '{get_slide_path(DEFAULT_SLIDE)}' not found. Provide a slide file or set DEFAULT_SLIDE."
        )
    if not os.path.exists(get_heatmap_path(DEFAULT_HEATMAP)):
        print(
            f"Warning: '{get_heatmap_path(DEFAULT_HEATMAP)}' not found. Provide a heatmap file or set DEFAULT_HEATMAP."
        )
        
    app.run(debug=True, host='0.0.0.0', port=5000)

