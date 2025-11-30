import os
import urllib.request

SOIL_TYPES = ["Clay", "Sandy", "Silty", "Peaty", "Chalky", "Loamy"]
BASE_DIR = "dataset"

os.makedirs(BASE_DIR, exist_ok=True)

def download_images():
    for soil in SOIL_TYPES:
        folder = os.path.join(BASE_DIR, soil)
        os.makedirs(folder, exist_ok=True)

        print(f"\nDownloading images for: {soil}")

        for i in range(15):  
            url = f"https://source.unsplash.com/random/400x400/?soil,{soil.lower()}"
            save_path = os.path.join(folder, f"{soil}_{i}.jpg")

            try:
                urllib.request.urlretrieve(url, save_path)
                print(f"✔ Saved {save_path}")
            except Exception as e:
                print(f"Failed {save_path}: {e}")

if __name__ == "__main__":
    download_images()
    print("\nDownload Complete!")
