import requests
from bs4 import BeautifulSoup
import os

GALLERY_URLS = [
    "https://www.sviguns.com/zenphoto/page/archive/2021-05/",
    "https://www.sviguns.com/zenphoto/page/archive/2019-06/",
    "https://www.sviguns.com/zenphoto/page/archive/2018-08/",
    "https://www.sviguns.com/zenphoto/page/archive/2018-06/",
    "https://www.sviguns.com/zenphoto/page/archive/2018-05/",
    "https://www.sviguns.com/zenphoto/page/archive/2018-04/",
    "https://www.sviguns.com/zenphoto/page/archive/2017-01/",
    "https://www.sviguns.com/zenphoto/page/archive/2000-01/",
    # ... add all your URLs here
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_image(img_src):
    """Download the image and save it to the 'downloaded_images' directory."""
    base_url = "https://www.sviguns.com"
    img_url = base_url + img_src
    response = requests.get(img_url, stream=True, headers=HEADERS)
    
    clean_filename = os.path.basename(img_src).split('?')[0]
    filename = os.path.join("downloaded_images", clean_filename)
    
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

def extract_images_from_page(soup):
    """Extracts all image URLs from the provided BeautifulSoup object."""
    images = []
    for img in soup.find_all("img"):
        img_src = img.get("src")
        # Exclude the banner image
        if "banniere3.jpg" not in img_src:
            images.append(img_src)
    return images

import time

def scrape_gallery(gallery_url):
    base_url = "https://www.sviguns.com"
    page_number = 1

    while True:
        current_gallery_url = f"{gallery_url}{page_number}/" if page_number > 1 else gallery_url
        response = requests.get(current_gallery_url, headers=HEADERS)

        if response.status_code == 404:
            print(f"Finished processing gallery pages up to {page_number - 1}.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find links that wrap around thumbnail images
        for a_tag in soup.find_all("a", href=True):
            img_tag = a_tag.find("img", src=lambda s: "thumb.jpg" in s)
            if img_tag:
                thumbnail_page_url = base_url + a_tag["href"]
                
                print(f"Visiting thumbnail page: {thumbnail_page_url}")
                thumb_page_response = requests.get(thumbnail_page_url, headers=HEADERS)
                thumb_page_soup = BeautifulSoup(thumb_page_response.text, 'html.parser')
                
                full_image_tag = thumb_page_soup.find("img", src=lambda s: "_700.jpg" in s)
                if full_image_tag:
                    img_src = full_image_tag["src"]
                    print(f"Downloading image from: {img_src}")
                    download_image(img_src)
                else:
                    print(f"No full-sized image found on {thumbnail_page_url}")
                time.sleep(2)  # Introducing a delay of 2 seconds between each thumbnail page request

        # Go to the next page number
        page_number += 1
        time.sleep(5)  # Introducing a delay of 5 seconds between each gallery page request


def main():
    if not os.path.exists("downloaded_images"):
        os.makedirs("downloaded_images")
    
    for gallery_url in GALLERY_URLS:
        scrape_gallery(gallery_url)

if __name__ == "__main__":
    main()
