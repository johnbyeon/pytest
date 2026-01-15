
from PIL import Image

def get_lego_colors():
    """
    Returns a dictionary of common Lego colors.
    Key: LDraw Color ID
    Value: (R, G, B) tuple
    This is a simplified palette.
    """
    return {
        0: (27, 42, 52),     # Black
        1: (45, 87, 168),    # Blue
        2: (51, 150, 68),    # Green
        4: (200, 36, 40),    # Red
        14: (228, 203, 76),  # Yellow
        15: (254, 254, 254), # White
        19: (180, 155, 114), # Tan
        28: (211, 187, 142), # Flesh
        71: (160, 165, 169), # Light Bluish Gray
        72: (108, 110, 107), # Dark Bluish Gray
        320: (170, 48, 48),  # Dark Red
    }

def find_closest_lego_color(rgb, lego_palette):
    """
    Finds the closest Lego color for a given RGB value.
    Uses simple Euclidean distance.
    """
    min_dist = float('inf')
    closest_id = 0
    
    r1, g1, b1 = rgb
    
    for color_id, (r2, g2, b2) in lego_palette.items():
        dist = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest_id = color_id
            
    return closest_id

def image_to_ldr(image_path, output_filename, width_studs=32):
    """
    Converts an image to a Lego mosaic LDR file.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        return

    # Resize image to match the desired stud width (maintain aspect ratio)
    w, h = img.size
    aspect_ratio = h / w
    height_studs = int(width_studs * aspect_ratio)
    img = img.resize((width_studs, height_studs), Image.Resampling.NEAREST)
    img = img.convert("RGB")
    
    lego_palette = get_lego_colors()
    
    # 1x1 Plate LDraw ID
    part_id = "3024.dat" 
    # Matrix: 1 0 0 0 1 0 0 0 1
    rotation_matrix = "1 0 0 0 1 0 0 0 1"
    
    with open(output_filename, 'w') as f:
        f.write(f"0 Mosaic created from {image_path}\n")
        f.write(f"0 Name: {output_filename}\n")
        
        pixels = img.load()
        
        # Iterate over pixels
        # In LDraw, Z is depth. Let's lay it flat on X-Z plane.
        # X axis: Left-Right
        # Z axis: Front-Back (Top-Bottom of image)
        # Y axis: Up-Down (Height). We will keep Y=0 for a flat baseplate.
        
        for y in range(height_studs):
            for x in range(width_studs):
                r, g, b = pixels[x, y]
                color_id = find_closest_lego_color((r, g, b), lego_palette)
                
                # Calculate coordinates
                # 1 stud = 20 LDraw units
                ldraw_x = x * 20
                ldraw_z = y * 20
                ldraw_y = 0 
                
                line = f"1 {color_id} {ldraw_x} {ldraw_y} {ldraw_z} {rotation_matrix} {part_id}\n"
                f.write(line)

    print(f"Successfully created {output_filename} ({width_studs}x{height_studs} studs)")

if __name__ == "__main__":
    # You can change the image path here
    # Start with a dummy file check or ask user to provide one
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        image_to_ldr(img_path, "mosaic.ldr")
    else:
        print("Usage: python image_to_ldr.py <path_to_image>")
