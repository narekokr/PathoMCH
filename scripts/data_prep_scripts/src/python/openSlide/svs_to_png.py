import os
# from openslide import *
# from PIL import Image

def convert_svs_to_png(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.svs'):
                svs_path = os.path.join(root, file)
                png_path = os.path.join(output_dir, os.path.splitext(file)[0] + '.png')

                slide = openslide.OpenSlide(svs_path)
                # Get the slide's dimensions
                dimensions = slide.level_dimensions[0]

                # Read the whole slide at level 0
                slide_image = slide.read_region((0, 0), 0, dimensions)
                slide_image = slide_image.convert("RGB")  # Convert to RGB mode

                slide_image.save(png_path, 'PNG')
                print(f"Converted {svs_path} to {png_path}")

# Example usage
input_dir = '/path/to/input_directory'
output_dir = '/path/to/output_directory'

convert_svs_to_png(input_dir, output_dir)
