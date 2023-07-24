import os
import uuid
from pathlib import Path

from sanic import Sanic, response
from sanic.request import Request
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


@app.post("/images/upload")
async def upload_image(request: Request):
    """
    Upload an image to the server.

    This endpoint allows you to upload an image to the server's image directory.

    openapi:
    ---
    operationId: fooDots
    tags:
      - CRUD
    requestBody:
      content:
        image/*:
          schema:
            type: string
            format: binary
      required: true
    responses:
      200:
        description: Upload successful.
        schema:
          type: object
          properties:
            message:
              type: string
              description: A success message.
            image_id:
              type: string
              description: The unique ID assigned to the uploaded image.
            image_path:
              type: string
              description: The URL to access the uploaded image.

      400:
        description: No file provided or invalid file type.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating that no file was provided or the file type is invalid.

    requestBody:
      content:
        application/x-www-form-urlencoded:
          schema:
            type: object
            properties:
              image:
                type: image
                description: The image to be replaced (required).
              category:
                type: string
                description: The category of the image (optional).
              number:
                type: string
                description: The number of the image (optional).
              title:
                type: string
                description: The title of the image (optional).
              name:
                type: string
                description: The name of the image (optional).
              content:
                type: string
                description: The content of the image (optional).
              price:
                type: string
                description: The price of the image (optional).
              status:
                type: string
                description: The status of the image (optional).
              situation:
                type: string
                description: The situation of the image (optional).
    """
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

    # TODO
    image_info = ImageInfo(request.form)
    return json(
        {
            "message": "Upload successful",
            "image_id": image_id,
            "image_path": f"http://{request.host}/{image_path}",
        }
    )


@app.put("/images/<image_name>")
async def replace_image(request: Request, image_name: str):
    """
    Replace an image by its name.

    This endpoint allows you to replace an existing image in the server's image directory.
    Note: If you want to update information only and not the image itself, \
        do not include the 'image' parameter in the request.

    openapi:
    ---
    operationId: fooDots
    tags:
      - CRUD
    parameters:
      - name: image_name
        description: The name of the image to be replaced.
        in: path
        type: string
        required: true
    requestBody:
      content:
        image/*:
          schema:
            type: string
            format: binary
      required: true
    responses:
      200:
        description: Image replaced successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: A success message.
      304:
        description: Nothing changed.
        schema:
          type: object
          properties:
            message:
              type: string
              description: A message indicating that nothing was changed.
      400:
        description: Invalid file type.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating that only image files are allowed.
      404:
        description: Image not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating the image was not found.
      500:
        description: Failed to replace image.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating the replacement failure.
    requestBody:
      content:
        application/x-www-form-urlencoded:
          schema:
            type: object
            properties:
              image:
                type: image
                description: The image to be replaced (optional).
              category:
                type: string
                description: The category of the image (optional).
              number:
                type: string
                description: The number of the image (optional).
              title:
                type: string
                description: The title of the image (optional).
              name:
                type: string
                description: The name of the image (optional).
              content:
                type: string
                description: The content of the image (optional).
              price:
                type: string
                description: The price of the image (optional).
              status:
                type: string
                description: The status of the image (optional).
              situation:
                type: string
                description: The situation of the image (optional).
    """
    try:
        uploaded_file = request.files["image"][0]
        if not uploaded_file.type.startswith("image/"):
            return json(
                {"error": "Invalid file type. Only images allowed."}, status=400
            )
        image_path = IMAGE_DIRECTORY.joinpath(image_name).absolute()

        if os.path.exists(image_path):
            try:
                # Save the new image file, overwriting the existing one
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.body)
            except OSError as e:
                return response.json(
                    {"error": f"Failed to replace image: {str(e)}"}, status=500
                )
        else:
            return response.json({"error": "Image not found"}, status=404)
    except KeyError:
        # Image file not provided
        if all(v == [""] for v in request.form.values()):
            return response.json({"message": "Nothing Changed"}, status=304)

    # TODO
    image_info = ImageInfo(request.form)
    return response.json({"message": "Image replaced successfully"})


@app.get("/images/<image_name>")
async def get_image(request: Request, image_name: str):
    """
    Get an image by its name.

    This endpoint allows you to retrieve an image from the server's image directory.

    openapi:
    ---
    operationId: fooDots
    tags:
      - CRUD
    parameters:
      - name: image_name
        description: The name of the image to be retrieved.
        in: path
        type: string
        required: true
    responses:
      200:
        description: Image found and returned successfully.
        content:
          image/*:
            schema:
              type: string
              format: binary
      404:
        description: Image not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating the image was not found.
    """
    image_path = IMAGE_DIRECTORY.joinpath(image_name).absolute()

    try:
        if not image_path.exists():
            return json({"error": "Image not found"}, status=404)
        return await file(str(image_path))
    except FileNotFoundError:
        return json({"error": "Image not found"}, status=404)


@app.delete("/images/<image_name>")
async def delete_image(request: Request, image_name: str):
    """
    Delete an image by its name.

    This endpoint allows you to delete an image from the server's image directory.

    openapi:
    ---
    operationId: fooDots
    tags:
      - CRUD
    parameters:
      - name: image_name
        description: The name of the image to be deleted.
        in: path
        type: string
        required: true
    responses:
      200:
        description: Image deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: A success message.
      404:
        description: Image not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating the image was not found.
      500:
        description: Failed to delete image.
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating the deletion failure.
    """
    image_path = IMAGE_DIRECTORY.joinpath(image_name).absolute()

    if os.path.exists(image_path):
        try:
            os.remove(image_path)
            return response.json({"message": "Image deleted successfully"})
        except OSError as e:
            return response.json(
                {"error": f"Failed to delete image: {str(e)}"}, status=500
            )
    else:
        return response.json({"error": "Image not found"}, status=404)


@app.get("/")
async def health_check(request):
    """This is a simple health check API

    openapi:
    ---
    operationId: fooDots
    tags:
      - healthCheck
    responses:
        200:
            description: Server is running
            content:
                text/plain:
                    schema:
                        type: string
    """
    return response.text("Server is running \n")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
