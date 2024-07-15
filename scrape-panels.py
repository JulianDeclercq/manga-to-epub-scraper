import os
import requests
from bs4 import BeautifulSoup
import argparse


# Function to download images from a given URL
def download_images_from_url(url, directory):
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Send a request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image tags
    img_tags = soup.find_all('img')

    # Download each image
    for img in img_tags:
        img_url = img['src']
        if img_url.endswith(('.jpg', '.jpeg')):
            # Get the image file name
            img_name = os.path.basename(img_url)
            img_path = os.path.join(directory, img_name)

            # Download the image and save it
            img_data = requests.get(img_url).content
            with open(img_path, 'wb') as handler:
                handler.write(img_data)

    print(f"Finished downloading chapter {os.path.basename(directory)}.")


# Main function to handle argument parsing and downloading
def main(start_chapter, end_chapter):
    base_url = "https://ww10.readonepiece.com/chapter/one-piece-digital-colored-comics-chapter-"
    for chapter in range(start_chapter, end_chapter + 1):
        url = f"{base_url}{chapter}/"
        directory = f"one-piece-colored-{chapter}"
        print(f"Downloading images for chapter {chapter}...")
        download_images_from_url(url, directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download One Piece Digital Colored Comics chapters (inclusive range).')
    parser.add_argument('start_chapter', type=int, help='The starting chapter number (inclusive)')
    parser.add_argument('end_chapter', type=int, help='The ending chapter number (inclusive)')

    args = parser.parse_args()
    main(args.start_chapter, args.end_chapter)
