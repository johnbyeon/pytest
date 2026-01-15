
import sys

def visualize_ldr(filename):
    """
    Simple ASCII visualizer for LDR files (Top-down view).
    """
    coords = []
    min_x, max_x = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if not parts or parts[0] != '1':
                    continue
                
                # LDraw line: 1 <colour> <x> <y> <z> ...
                try:
                    x = float(parts[2])
                    z = float(parts[4])
                    coords.append((x, z))
                    
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_z = min(min_z, z)
                    max_z = max(max_z, z)
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    if not coords:
        print("No bricks found in file.")
        return

    # Normalize to grid
    # Assuming 20 LDu grid size
    grid_size = 20
    
    width = int((max_x - min_x) / grid_size) + 1
    height = int((max_z - min_z) / grid_size) + 1
    
    # Cap size for terminal display
    if width > 100 or height > 100:
        print(f"Model is too large for terminal visualization ({width}x{height}). Scaling down...")
        scale = max(width, height) / 80
    else:
        scale = 1
        
    scaled_width = int(width / scale) + 1
    scaled_height = int(height / scale) + 1
    
    grid = [[' ' for _ in range(scaled_width)] for _ in range(scaled_height)]
    
    for x, z in coords:
        # Map to grid indices
        ix = int((x - min_x) / grid_size / scale)
        iz = int((z - min_z) / grid_size / scale)
        
        if 0 <= ix < scaled_width and 0 <= iz < scaled_height:
            grid[iz][ix] = '█' # Block character

    print(f"--- Visualization of {filename} ---")
    for row in grid:
        print("".join(row))
    print("-----------------------------------")

if __name__ == "__main__":
    filename = "relief.ldr"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    visualize_ldr(filename)
