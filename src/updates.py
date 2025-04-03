from pathlib import Path
import json
import requests
from PIL import Image
from io import BytesIO
import os

def auto_update():
    """is called on system start, if auto update is enabled, calls update_all()"""
    datapath = str(Path(__file__).parent / "data.json")
    with open(datapath, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            if data["auto-updates"] == True:
                print("auto updates are on, updating")
                update_all()
            else:
                print("auto updates are off")

        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {datapath}")

def is_up_to_date():
    """verifies if the version in data.json is the latest one, returns True if it is"""
    return False


def update_all():
    """updates everything"""
    if not(is_up_to_date()):
        download_file()


def update_category(name):
    """updates all the wallpapers from the given category"""
    wallpapers_path = Path(__file__).parent.parent / "wallpapers" / name
    list_path = f"{wallpapers_path}/list.json"
    update_path = f"https://github.com/princess-wawa/nyarch-wallpapers/blob/main/wallpapers/{name}/list.json"
    
    download_file(update_path, list_path)

    with open(list_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {list_path}")
    
    for e in data:
        dark_path = f"{wallpapers_path}/{e['files']}_dark.jpg"
        light_path = f"{wallpapers_path}/{e['files']}_light.jpg"
        if not(os.path.exists(dark_path)):
            download_and_crop_image(e["dark"]["source-link"], dark_path)
        if not(os.path.exists(light_path)):
            download_and_crop_image(e["light"]["source-link"], light_path)

        


def download_file(url, filename):
    """
    Downloads a file from a given URL and saves it with the specified filename.

    :param url: The URL of the file to download.
    :param filename: The name to save the file as.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File downloaded successfully: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def download_and_crop_image(url, save_path):
    """
    Downloads an image from a given URL, crops it to a 16:9 aspect ratio, and saves it as a JPG.

    :param url: The URL of the image to download.
    :param save_path: The path where the cropped image should be saved (must end with .jpg).
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check if the request was successful

        # Open the image using PIL
        image = Image.open(BytesIO(response.content)).convert("RGB")  # Ensure RGB mode for JPG

        # Get the original dimensions
        width, height = image.size
        target_aspect_ratio = 16 / 9

        # Calculate the new dimensions
        if width / height > target_aspect_ratio:
            # Crop width (too wide)
            new_width = int(height * target_aspect_ratio)
            left = (width - new_width) // 2
            right = left + new_width
            top, bottom = 0, height
        else:
            # Crop height (too tall)
            new_height = int(width / target_aspect_ratio)
            top = (height - new_height) // 2
            bottom = top + new_height
            left, right = 0, width

        # Crop the image
        cropped_image = image.crop((left, top, right, bottom))

        # Ensure the save path ends with ".jpg"
        if not save_path.lower().endswith(".jpg"):
            save_path += ".jpg"

        # Save the cropped image as a JPG with high quality
        cropped_image.save(save_path, "JPEG", quality=95)
        print(f"Image successfully downloaded, cropped, and saved as JPG: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
    except Exception as e:
        print(f"Error processing the image: {e}")


update_category("updates")