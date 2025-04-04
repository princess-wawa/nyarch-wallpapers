from pathlib import Path
import json
import threading
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

            if data["auto-updates"] == "True":
                print("auto updates are on, updating")
                update_all()
            else:
                print("auto updates are off")

        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {datapath}")

def is_up_to_date():
    """verifies if the version in data.json is the latest one, returns True if it is"""
    try:
        response = requests.get("https://raw.githubusercontent.com/princess-wawa/nyarch-wallpapers/refs/heads/main/src/data.json")
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        latest_version = response.json()["version"]
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError:
        print("Response content is not valid JSON.")
    
    datapath = str(Path(__file__).parent / "data.json")
    with open(datapath, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            current_version = data["version"] 
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {datapath}")
    
    return latest_version == current_version



def update_all():
    """updates everything"""
    if not(is_up_to_date()):
        """updates all the wallpapers from the given category"""
        wallpapers_path = Path(__file__).parent.parent / "wallpapers"
        list_path = f"{wallpapers_path}/list.json"
        update_path = f"https://raw.githubusercontent.com/princess-wawa/nyarch-wallpapers/refs/heads/main/wallpapers/list.json"
        
        success = download_file(update_path, list_path)
        
        if success:
            with open(list_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {list_path}")
            
            threads = []
            updated_something = False
            for e in data:
                dark_path = f"{wallpapers_path}/{e['files']}_dark.jpg"
                light_path = f"{wallpapers_path}/{e['files']}_light.jpg"
                if not(os.path.exists(dark_path)):
                    updated_something = True
                    threads.append(async_download_and_crop_image(e["dark"]["source-link"], dark_path))
                if not(os.path.exists(light_path)):
                    updated_something = True
                    threads.append(async_download_and_crop_image(e["light"]["source-link"], light_path))
            
            if updated_something:
                print("waiting for all threads to finish")
                for t in threads:
                    t.join()
                print("all threads finished")
            
        data_path = str(Path(__file__).parent / "data.json")
        download_file("https://raw.githubusercontent.com/princess-wawa/nyarch-wallpapers/refs/heads/main/src/data.json",data_path)
    else:
        print("up to date")


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
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False


def async_download_and_crop_image(url, save_path):
    """
    Asynchronously runs the download_and_crop_image function in a separate thread.

    :param url: The URL of the image to download.
    :param save_path: The path where the cropped image should be saved.
    """
    thread = threading.Thread(target=download_and_crop_image, args=(url, save_path))
    thread.start()
    return thread  # Optional: return the thread if you want to join or monitor it


def download_and_crop_image(url, save_path):
    """
    Downloads an image from a given URL, crops it to a 16:9 aspect ratio,
    replaces transparency with white if needed, and saves it as a JPG.

    :param url: The URL of the image to download.
    :param save_path: The path where the cropped image should be saved (should end with .jpg).
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Open the image using PIL
        image = Image.open(BytesIO(response.content))

        # Handle transparency by converting to white background
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            background = Image.new("RGB", image.size, (255, 255, 255))
            image = image.convert("RGBA")
            background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
            image = background
        else:
            image = image.convert("RGB")

        # Get original size
        width, height = image.size
        target_aspect_ratio = 16 / 9

        # Calculate crop box
        if width / height > target_aspect_ratio:
            new_width = int(height * target_aspect_ratio)
            left = (width - new_width) // 2
            box = (left, 0, left + new_width, height)
        else:
            new_height = int(width / target_aspect_ratio)
            top = (height - new_height) // 2
            box = (0, top, width, top + new_height)

        # Crop to 16:9
        cropped = image.crop(box)

        # Ensure .jpg extension
        if not save_path.lower().endswith(".jpg"):
            save_path += ".jpg"

        # Save as JPEG
        cropped.save(save_path, "JPEG", quality=95)
        print(f"Image downloaded, cropped to 16:9, and saved as JPG: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
    except Exception as e:
        print(f"Error processing the image: {e}")


if __name__ == "__main__":
    update_all()