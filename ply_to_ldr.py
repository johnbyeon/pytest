
import trimesh
import numpy as np

def get_lego_colors():
    # Simplified Lego Palette
    return {
        0: (27, 42, 52),     # Black
        1: (45, 87, 168),    # Blue
        2: (51, 150, 68),    # Green
        4: (200, 36, 40),    # Red
        14: (228, 203, 76),  # Yellow
        15: (254, 254, 254), # White
        71: (160, 165, 169), # Light Bluish Gray
    }

def mesh_to_ldr(mesh_filename, output_filename, resolution=32):
    """
    Converts a 3D mesh file (.ply, .obj, etc.) to a Lego LDR file.
    resolution: Number of voxels along the longest axis.
    """
    print(f"Loading mesh: {mesh_filename}")
    try:
        mesh = trimesh.load(mesh_filename)
    except Exception as e:
        print(f"Error loading mesh: {e}")
        return

    # Voxelize the mesh
    print(f"Voxelizing mesh with resolution {resolution}...")
    # Calculate pitch (size of one voxel) based on resolution
    max_dim = np.max(mesh.extents)
    pitch = max_dim / resolution
    
    voxelized = mesh.voxelized(pitch=pitch)
    
    # Fill internal structure for solidity (optional, but good for building)
    # voxelized = voxelized.fill() 
    
    # Get indices of filled voxels
    matrix = voxelized.matrix # boolean 3d array
    indices = np.argwhere(matrix)
    
    # LDraw constants
    # 1x1 Brick
    part_id = "3001.dat"  # 2x4 brick default? No, let's use 1x1 brick for voxels mostly
    part_id = "3005.dat" # 1x1 Brick
    
    # Dimensions in LDraw Units
    # 1x1 Brick size: 20 x 20 width (studs), 24 height
    ldraw_width = 20
    ldraw_height = 24
    
    rotation_matrix = "1 0 0 0 1 0 0 0 1"
    
    default_color = 4 # Red
    
    count = 0
    with open(output_filename, 'w') as f:
        f.write(f"0 Voxel Model generated from {mesh_filename}\n")
        f.write(f"0 Name: {output_filename}\n")
        
        # Center the model
        center_x = (matrix.shape[0] * ldraw_width) / 2
        center_z = (matrix.shape[2] * ldraw_width) / 2
        
        for x, y, z in indices:
            # Swap axes to match Lego coordinate system usually:
            # Voxel Z (up) -> Lego -Y (up)
            # Voxel X, Y -> Lego X, Z
            
            # Note: trimesh voxel indices x,y,z
            # Let's map: 
            # Py X -> Lego X
            # Py Y -> Lego -Y (Height)
            # Py Z -> Lego Z
            
            lx = x * ldraw_width - center_x
            ly = - (y * ldraw_height) # Stack upwards (negative Y)
            lz = z * ldraw_width - center_z
            
            # Simple optimization: Checkerboard pattern for structural integrity?
            # For now, just place 1x1 bricks.
            
            line = f"1 {default_color} {lx} {ly} {lz} {rotation_matrix} {part_id}\n"
            f.write(line)
            count += 1
            
    print(f"Successfully created {output_filename} with {count} bricks.")

if __name__ == "__main__":
    import sys
    mesh_path = "output_3d.ply"
    if len(sys.argv) > 1:
        mesh_path = sys.argv[1]
    
    mesh_to_ldr(mesh_path, "voxel_model.ldr", resolution=32)
