import numpy as np
from PIL import Image
from collections import Counter


def check_img_is_mainly_one_color(image_path, variance_threshold=0.02):
    # Open the image and convert it to RGB
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)

    # Reshape the image array to a list of RGB tuples
    pixels = img_array.reshape(-1, 3)

    # Count the occurrences of each color
    pixel_counts = Counter(map(tuple, pixels))

    # Find the most common color
    most_common_color, most_common_count = pixel_counts.most_common(1)[0]

    # Calculate the percentage of pixels that match the most common color within the variance
    total_pixels = pixels.shape[0]
    variance_count = 0

    for color, count in pixel_counts.items():
        if np.all(np.abs(np.array(color) - np.array(most_common_color)) <= 255 * variance_threshold):
            variance_count += count

    percentage_variance = variance_count / total_pixels

    # Print the result
    if percentage_variance >= (1 - variance_threshold):
        # print(f"The image is mainly one color: {most_common_color} with {percentage_variance * 100:.2f}% similarity.")
        return True
    else:
        # print(
        #     f"The image is not mainly one color. The most common color is {most_common_color} with
        #     {percentage_variance * 100:.2f}% similarity.")
        return False


img_path= "/home/mathias/DSitLS/mainly_one_color_image"
check_img_is_mainly_one_color(img_path)