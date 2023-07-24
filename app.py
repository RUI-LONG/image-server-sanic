import os
import uuid
from pathlib import Path

from sanic import Sanic, response
from sanic.response import json, file

app = Sanic(__name__)

IMAGE_DIRECTORY = Path("images")


class ImageInfo:
    def __init__(self, form_data={}):
        # 類別:
        self.category = form_data.get("category", "")
        # 編號:
        self.number = form_data.get("number", "")
        # 劇名:
        self.title = form_data.get("title", "")
        # 名稱:
        self.name = form_data.get("name", "")
        # 內容:(註:服裝的內容物)
        self.content = form_data.get("content", "")
        # 價格:
        self.price = form_data.get("price", "")
        # 狀態:(註:服裝的新舊情況)
        self.status = form_data.get("status", "")
        # 情境:
        self.situation = form_data.get("situation", "")


@app.post("/image/upload")
async def upload_image(request):
    """"""
    # Ensure the request is a POST request and contains a file named 'image'
    if "image" not in request.files:
        return json({"error": "No file provided"}, status=400)

    uploaded_file = request.files["image"][0]
    if not uploaded_file.type.startswith("image/"):
        return json({"error": "Invalid file type. Only images allowed."}, status=400)

    image_id = uuid.uuid4().hex
    _, file_extension = os.path.splitext(uploaded_file.name)
    # filename = f"{hash(uploaded_file.body)}{file_extension}".replace("-", "")
    filename = f"{image_id}{file_extension}".replace("-", "")

    image_path = str(IMAGE_DIRECTORY.joinpath(filename)).replace("\\", "/")
    with open(image_path, "wb") as f:
        f.write(uploaded_file.body)

    image_info = ImageInfo(request.form)
    return json(
        {
            "message": "Upload successful",
            "image_id": image_id,
            "image_path": f"http://{request.host}/{image_path}",
        }
    )


@app.get("/images/<image_name>")
async def get_image(request, image_name):
    """
    In this endpoint, clients can request images by providing their names as part of the URL path.
    The 'image_name' parameter is captured from the URL path, allowing us to identify the requested image.
    """
    image_path = IMAGE_DIRECTORY.joinpath(image_name).absolute()

    try:
        if not image_path.exists():
            return json({"error": "Image not found"}, status=404)
        return await file(str(image_path))
    except FileNotFoundError:
        # If the requested image is not found, we respond with a 404 error.
        return json({"error": "Image not found"}, status=404)


@app.get("/")
async def health_check(request):
    return response.text("Server is running \n")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
