import base64
import io
import os
import sys
from urllib import request

import helius
import ipfshttpclient
from fastapi import FastAPI, HTTPException
import cv2
from PIL import Image
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from jsonify.convert import jsonify

from cartoonize import WB_Cartoonize
from model import CartoonizeRequest

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    # Add more allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def convert_base64_to_image(base64_string):
    # Remove the data:image/png;base64 prefix
    base64_string = base64_string.replace("data:image/png;base64,", "")

    # Decode the base64 string using urlsafe_b64decode
    image_bytes = base64.urlsafe_b64decode(base64_string)

    # Create a BytesIO object
    image_buffer = io.BytesIO(image_bytes)

    # Open the image using PIL
    image = Image.open(image_buffer)

    # Save the image to a file (optional)
    image.save("image.png")

    return image


@app.post("/cartoonize")
async def cartoonize(request: CartoonizeRequest):
    try:
        convert_base64_to_image(request.file)
        img = cv2.imread('image.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cartoon_image = wb_cartoonizer.infer(img)
        image = Image.fromarray(cartoon_image)
        image.save("image.png")
        with open("image.png", "rb") as image_file:
            data = base64.b64encode(image_file.read())
            return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal error")