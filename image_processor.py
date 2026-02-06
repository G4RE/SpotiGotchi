import requests
from io import BytesIO
from PIL import Image

MATRIX_SIZE = (64, 64)

def album_art_to_image(source):
    if source.startswith("http"):
        response = requests.get(source)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(source)

    img = img.convert("RGB")
    img = img.resize(MATRIX_SIZE, Image.BICUBIC)
    return img
