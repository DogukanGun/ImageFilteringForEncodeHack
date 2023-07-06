import io
import os
import sys
import uuid
from fastapi import FastAPI
import cv2
from PIL import Image
import numpy as np

from cartoonize import WB_Cartoonize

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


opts = dict()
opts["gpu"] = True
opts["output_folder"] = "static/cartoonized_images"

sys.path.insert(0, '')

wb_cartoonizer = WB_Cartoonize(os.path.abspath("saved_models/"), opts['gpu'])


def convert_bytes_to_image(img_bytes):
    """Convert bytes to numpy array

    Args:
        img_bytes (bytes): Image bytes read from flask.

    Returns:
        [numpy array]: Image numpy array
    """

    pil_image = Image.open(io.BytesIO(img_bytes))
    if pil_image.mode == "RGBA":
        image = Image.new("RGB", pil_image.size, (255, 255, 255))
        image.paste(pil_image, mask=pil_image.split()[3])
    else:
        image = pil_image.convert('RGB')

    image = np.array(image)

    return image


@app.post("/cartoonize")
async def cartoonize(file: str):

    image = convert_bytes_to_image(file.encode("utf-8"))

    img_name = str(uuid.uuid4())

    cartoon_image = wb_cartoonizer.infer(image)

    cartoonized_img_name = os.path.join(opts['CARTOONIZED_FOLDER'], img_name + ".jpg")
    cv2.imwrite(cartoonized_img_name, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
