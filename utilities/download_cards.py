import os
import json
import requests
from PIL import Image

# Directory to save images
output_dir = "../genetic_apex_images"
os.makedirs(output_dir, exist_ok=True)

# Load HAR file
har_file = "apex.har"  # Replace with the path to your HAR file

with open(har_file, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

# Extract image URLs from HAR file
image_urls = []
for entry in har_data['log']['entries']:
    url = entry['request']['url']
    if url.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        image_urls.append(url)

# Function to download images
def download_images(image_urls, folder):
    webp_images = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for img_url in image_urls:
        img_name = os.path.join(folder, os.path.basename(img_url))
        print(f"Downloading {img_url}...")

        # Download image with headers
        response = requests.get(img_url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            with open(img_name, 'wb') as f:
                f.write(response.content)
            print(f"Saved to {img_name}")

            # Track .webp images for conversion
            if img_name.endswith('.webp'):
                webp_images.append(img_name)
        else:
            print(f"Failed to download {img_url}. Status code: {response.status_code}")

    return webp_images

# Convert .webp to .png
def convert_webp_to_png(webp_images, folder):
    for webp_image in webp_images:
        png_image = os.path.splitext(webp_image)[0] + ".png"
        img = Image.open(webp_image)
        img.save(png_image, "PNG")
        print(f"Converted {webp_image} to {png_image}")

# Download images
webp_images = download_images(image_urls, output_dir)

# Convert .webp images to .png
convert_webp_to_png(webp_images, output_dir)
