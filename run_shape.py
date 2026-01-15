
import torch
from diffusers import ShapEPipeline
from diffusers.utils import export_to_ply
import sys

def generate_3d(prompt, output_filename="output_3d.ply"):
    print(f"Loading Shap-E model... (This may take a while on first run)")
    
    # MPS 가속을 위해 device 설정
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
        
    print(f"Using device: {device}")

    # Load pipeline
    pipe = ShapEPipeline.from_pretrained("openai/shap-e", torch_dtype=torch.float32)
    pipe = pipe.to(device)

    print(f"Generating 3D model for prompt: '{prompt}'...")
    
    # Generate
    # num_inference_steps=64 is a good balance between speed and quality
    images = pipe(
        prompt, 
        guidance_scale=15.0, 
        num_inference_steps=64, 
        frame_size=256,
        output_type="mesh" # Output as mesh directly
    ).images

    # Save the first result
    ply_path = export_to_ply(images[0], output_filename)
    print(f"Successfully saved 3D model to: {output_filename}")

if __name__ == "__main__":
    prompt = "a lego brick"
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        
    generate_3d(prompt)
