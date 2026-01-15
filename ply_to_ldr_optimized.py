
import trimesh
import numpy as np

def get_lego_colors():
    # Simplified Lego Palette
    return {
        4: (200, 36, 40),    # Red
        2: (51, 150, 68),    # Green
        1: (45, 87, 168),    # Blue
    }

def mesh_to_ldr_optimized(mesh_filename, output_filename, resolution=32):
    print(f"Loading mesh: {mesh_filename}")
    try:
        mesh = trimesh.load(mesh_filename)
        # Normalize mesh to unit cube first? Shap-E output is mostly normalized.
    except Exception as e:
        print(f"Error loading mesh: {e}")
        return

    print(f"Voxelizing mesh with resolution {resolution}...")
    max_dim = np.max(mesh.extents)
    pitch = max_dim / resolution
    voxelized = mesh.voxelized(pitch=pitch)
    
    # Fill internal structure for solidity
    voxelized = voxelized.fill()
    matrix = voxelized.matrix # boolean 3d array (x, y, z)
    
    # LDraw Dimensions
    ldraw_width = 20
    ldraw_height = 24
    rotation_matrix = "1 0 0 0 1 0 0 0 1"
    default_color = 4
    
    # Center Model
    center_x = (matrix.shape[0] * ldraw_width) / 2
    center_z = (matrix.shape[2] * ldraw_width) / 2
    
    bricks = [] # List of (x, y, z, length)
    
    # Iterate Y (Height) and Z (Depth) first, then merge along X
    # In Voxel matrix: usually x, y, z. Let's assume y is Up in voxel space for a moment, 
    # but mesh orientation varies. Let's stick to trimesh's default.
    
    nx, ny, nz = matrix.shape
    
    # Simple Optimization: Merge along X axis
    for y in range(ny):
        for z in range(nz):
            current_run_start = -1
            for x in range(nx):
                is_filled = matrix[x, y, z]
                
                if is_filled:
                    if current_run_start == -1:
                        current_run_start = x
                else:
                    if current_run_start != -1:
                        # End of run, add brick
                        length = x - current_run_start
                        bricks.append((current_run_start, y, z, length))
                        current_run_start = -1
            
            # End of row check
            if current_run_start != -1:
                length = nx - current_run_start
                bricks.append((current_run_start, y, z, length))

    # Write to LDR
    count = 0
    with open(output_filename, 'w') as f:
        f.write(f"0 Optimized Voxel Model from {mesh_filename}\n")
        f.write(f"0 Name: {output_filename}\n")
        
        for bx, by, bz, length in bricks:
            # We have lengths like 1, 2, 3, 4, 5...
            # Need to break down into available bricks: 1x1, 1x2, 1x3, 1x4, 2x4...
            # For simplicity, let's just use 1xN beams/bricks logic or naive stacking
            
            current_x = bx
            remaining_len = length
            
            while remaining_len > 0:
                # Greedy choice: Try largest brick first
                # Available 1xN bricks: 1x8, 1x6, 1x4, 1x3, 1x2, 1x1
                # IDs: 3008, 3009, 3622, 3623, 3004, 3005
                
                brick_len = 0
                part_id = ""
                
                if remaining_len >= 4:
                    brick_len = 4
                    part_id = "3010.dat" # 1x4 Brick
                elif remaining_len >= 3:
                    brick_len = 3
                    part_id = "3622.dat" # 1x3 Brick
                elif remaining_len >= 2:
                    brick_len = 2
                    part_id = "3004.dat" # 1x2 Brick
                else:
                    brick_len = 1
                    part_id = "3005.dat" # 1x1 Brick
                
                # Calculate LDraw Position
                # Center of the brick
                # Start X (left edge) = current_x * 20
                # Center X = Start X + (brick_len * 20) / 2 - 10 (offset to match stud center)
                # Actually, LDraw origin for bricks is usually the center of the stud (1x1) or center of the brick.
                # For 1x1: Origin is center.
                # For 1x2: Origin is often between studs.
                # Standard practice: Place based on stud units.
                
                # Careful: LDraw parts origin varies.
                # Just assuming standard placement logic:
                # X position should be: (current_x * 20) + (brick_len * 20 / 2) - 10 - center_offset
                
                # Simplified: Let's assume naive placement relative to 0
                # (This might need tweaking for exact alignment in Studio)
                
                # Correct Logic for Studs:
                # 1x1 at 0
                # 1x2 at 10 (centered between 0 and 20)
                # 1x4 at 30
                # Formula: pos = (start_index * 20) + (brick_len * 10) - 10
                
                pos_x = (current_x * ldraw_width) + (brick_len * 10) - 10 - center_x
                pos_y = - (by * ldraw_height)
                pos_z = (bz * ldraw_width) - center_z
                
                line = f"1 {default_color} {pos_x} {pos_y} {pos_z} {rotation_matrix} {part_id}\n"
                f.write(line)
                
                remaining_len -= brick_len
                current_x += brick_len
                count += 1

    print(f"Successfully created {output_filename} with {count} merged bricks.")

if __name__ == "__main__":
    import sys
    mesh_path = "output_3d.ply"
    if len(sys.argv) > 1:
        mesh_path = sys.argv[1]
    
    mesh_to_ldr_optimized(mesh_path, "voxel_optimized.ldr", resolution=32)
