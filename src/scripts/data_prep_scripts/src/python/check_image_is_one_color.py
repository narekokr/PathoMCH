import numpy as np
from PIL import Image
from collections import Counter


def check_img_is_mainly_one_color(image_path, variance_threshold=0.02):
    img_array = np.array(image_path)

    # Flatten the image array to a 2D array where each row is an RGB value
    pixels = image_path.reshape(-1, 3)

    # Calculate the mean color
    mean_color = np.mean(pixels, axis=0)

    # Calculate the distance of each pixel to the mean color
    color_distances = np.linalg.norm(pixels - mean_color, axis=1)

    # Count the number of pixels within the allowed variance
    within_variance = np.sum(color_distances <= 255 * variance_threshold)

    # Calculate the percentage of pixels within the variance
    total_pixels = pixels.shape[0]
    percentage_within_variance = within_variance / total_pixels
    # Print the result
    if percentage_within_variance >= (1 - variance_threshold):
        # print(f"The image is mainly one color: {most_common_color} with {percentage_variance * 100:.2f}% similarity.")
        return True
    else:
        # print(
        #     f"The image is not mainly one color. The most common color is {most_common_color} with
        #     {percentage_variance * 100:.2f}% similarity.")
        return False
