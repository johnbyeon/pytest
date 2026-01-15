from PIL import Image

def get_lego_colors():
    """
    Returns a dictionary of common Lego colors.
    Key: LDraw Color ID
    Value: (R, G, B) tuple
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
    min_dist = float('inf')
    closest_id = 0
    r1, g1, b1 = rgb
    for color_id, (r2, g2, b2) in lego_palette.items():
        dist = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest_id = color_id
    return closest_id

def image_to_relief(image_path, output_filename, width_studs=32, max_height_plates=10):
    """
    Converts an image to a 3D Lego relief LDR file.
    Brightness determines height.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        return

    # Resize image
    w, h = img.size
    aspect_ratio = h / w
    height_studs = int(width_studs * aspect_ratio)
    img = img.resize((width_studs, height_studs), Image.Resampling.NEAREST)
    img_rgb = img.convert("RGB")
    img_gray = img.convert("L") # Grayscale for height map
    
    lego_palette = get_lego_colors()
    
    # Parts
    # 3024.dat = 1x1 Plate (Height = 8 LDu)
    # 3005.dat = 1x1 Brick (Height = 24 LDu = 3 Plates)
    part_id = "3024.dat" 
    plate_height_ldu = 8
    
    rotation_matrix = "1 0 0 0 1 0 0 0 1"
    
    # Standard Lego Plate dimensions
    stud_width_ldu = 20
    
    with open(output_filename, 'w') as f:
        f.write(f"0 Relief Model created from {image_path}\n")
        f.write(f"0 Name: {output_filename}\n")
        
        pixels_rgb = img_rgb.load()
        pixels_gray = img_gray.load()
        
        for z in range(height_studs):
            for x in range(width_studs):
                r, g, b = pixels_rgb[x, z]
                
                # Background Removal (Skip White-ish pixels)
                # Euclidean distance from White (255, 255, 255)
                dist_white = ((r - 255) ** 2 + (g - 255) ** 2 + (b - 255) ** 2) ** 0.5
                if dist_white < 30: # Threshold
                    continue
                
                brightness = pixels_gray[x, z] # 0 (black) to 255 (white)
                
                # Calculate height in plates (1 to max_height_plates)
                # Brighter = Higher
                height = int((brightness / 255) * max_height_plates) + 1
                
                color_id = find_closest_lego_color((r, g, b), lego_palette)
                
                # Base Position
                ldraw_x = x * stud_width_ldu
                ldraw_z = z * stud_width_ldu
                
                # Stack plates
                for h_idx in range(height):
                    # Y grows downwards in LDraw, so negative Y is Up.
                    # h_idx=0 is base, h_idx=1 is on top of base
                    ldraw_y = -(h_idx * plate_height_ldu)
                    
                    line = f"1 {color_id} {ldraw_x} {ldraw_y} {ldraw_z} {rotation_matrix} {part_id}\n"
                    f.write(line)

    print(f"Successfully created {output_filename} ({width_studs}x{height_studs} studs, Max Height: {max_height_plates} plates)")

if __name__ == "__main__":
    import sys
    img_path = "test_image.png" # Default
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        
    image_to_relief(img_path, "relief.ldr")
