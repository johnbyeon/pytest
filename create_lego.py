
def create_ldr_file(filename):
    """
    Creates a simple LDR file with a few Lego bricks stacked.
    LDraw coordinates:
    - Y axis is vertical (negative is Up, positive is Down).
    - 1 Lego unit (plate height) is 8 LDraw units.
    - 1 Brick height is 24 LDraw units (3 plates).
    - 1 Stud width is 20 LDraw units.
    """
    
    # LDraw line format: 1 <colour> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <i> <h> <part>
    # Matrix for no rotation: 1 0 0 0 1 0 0 0 1
    
    # 3001.dat is a 2x4 brick
    part_id = "3001.dat"
    rotation_matrix = "1 0 0 0 1 0 0 0 1"
    
    bricks = [
        # Color, x, y, z
        (4, 0, 0, 0),    # Red (Base)
        (1, 0, -24, 0),  # Blue (Stacked on top, -24 is 1 brick height up)
        (2, 0, -48, 0),  # Green (Stacked on top of blue)
    ]
    
    with open(filename, 'w') as f:
        f.write("0 Test Model Created by Python\n")
        f.write("0 Name: test_model.ldr\n")
        
        for color, x, y, z in bricks:
            line = f"1 {color} {x} {y} {z} {rotation_matrix} {part_id}\n"
            f.write(line)
            
    print(f"Successfully created {filename}")

if __name__ == "__main__":
    create_ldr_file("test_model.ldr")
