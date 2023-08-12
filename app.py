import os
import uuid
import random
from pathlib import Path

from sanic import Sanic, response
from sanic.request import Request
from sanic.response import json, file
from pymongo import MongoClient

app = Sanic(__name__)

# Connect to MongoDB
mongo_uri = os.getenv("DB_URL") or "mongodb://localhost:27017"
db_name = "image_db"
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db["images"]

IMAGE_DIRECTORY = Path("images")


def str2bool(s):
    if s.lower() in ("true", "1", "yes", "y", "on"):
        return True
    return False


class ImageInfo:
    def __init__(self, form_data={}):
        # 類別:
        self.category = form_data.get("category", "")
        # 編號:
        self.number = str(random.randint(0, 9999999)).zfill(7)
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
    filename = f"{image_id}{file_extension}".replace("-", "")

    image_path = str(IMAGE_DIRECTORY.joinpath(filename)).replace("\\", "/")
    with open(image_path, "wb") as f:
        f.write(uploaded_file.body)

    image_info = ImageInfo(request.form)
    image_data = {
        "image_id": image_id,
        "image_path": image_path,
        "info": {
            "category": image_info.category,
            "number": image_info.number,
            "title": image_info.title,
            "name": image_info.name,
            "content": image_info.content,
            "price": image_info.price,
            "status": image_info.status,
            "situation": image_info.situation,
        },
    }
    collection.insert_one(image_data)

    return json(
        {
            "message": "Upload successful",
            "image_id": image_id,
            "image_path": f"{image_path}",
            "full_image_path": f"http://{request.host}/{image_path}",
        }
    )


@app.get("/images/search")
async def search_images(request):
    """
    Search images by keyword (title or name) in MongoDB.

    This endpoint allows you to search for images by specifying keywords for the title or name in the query parameters.

    openapi:
    ---
    operationId: searchImages
    tags:
      - CRUD
    parameters:
      - name: title
        description: Keyword to search for in image titles.
        in: query
        type: string
      - name: name
        description: Keyword to search for in image names.
        in: query
        type: string
      - name: page_number
        description: Current page number, start from 1. Default is `1`.
        in: query
        type: boolean string
      - name: page_size
        description: Page size. Default is `25`.
        in: query
        type: boolean string
      - name: exactly_match
        description: When exact_match is set to `true`, only return exact matches. Default is `false`.
        in: query
        type: boolean string
      - name: is_random
        description: When is_random is set to `true`, return random matches. Default is `false`.
        in: query
        type: boolean string
    responses:
      200:
        description: Successfully retrieved search results.
        content:
          application/json:
            schema:
              type: object
              properties:
                results:
                  type: array
                  items:
                    type: object
                    properties:
                      info:
                        type: object
                        properties:
                          title:
                            type: string
                            description: The title of the image.
                          name:
                            type: string
                            description: The name of the image.
                    example:
                      results: [
                        {
                          info: {
                            title: "Beautiful Landscape",
                            name: "landscape.jpg"
                          }
                        },
                        {
                          info: {
                            title: "Cute Animals",
                            name: "animals.png"
                          }
                        }
                      ]
      400:
        description: Bad Request. Missing query parameter(s).
        schema:
          type: object
          properties:
            error:
              type: string
              description: An error message indicating missing query parameter(s).
    """
    title = request.args.get("title", "")
    name = request.args.get("name", "")
    page_number = int(request.args.get("page_number", "1")) - 1
    page_size = int(request.args.get("page_size", "25"))
    exactly_match = str2bool(request.args.get("exactly_match", "false"))
    is_random = str2bool(request.args.get("is_random", "false"))

    if not any([title, name]):
        return json({"error": "Missing query parameter"}, status=400)

    results = []
    query = {}

    if title:
        if exactly_match:
            query["info.title"] = title
        else:
            query["info.title"] = {"$regex": title, "$options": "i"}
    if name:
        if exactly_match:
            query["info.name"] = name
        else:
            query["info.name"] = {"$regex": name, "$options": "i"}

    total_count = collection.count_documents(query)

    skip = page_number * page_size
    limit = page_size

    if total_count == 0:
        return json({"results": [], "total_count": 0})

    if is_random:
        cursor = collection.find(query, {"_id": 0}).limit(limit * 2)
        results = random.sample([image_data for image_data in cursor], limit)

    else:
        cursor = collection.find(query, {"_id": 0}).skip(skip).limit(limit)
        results = [image_data for image_data in cursor]

    return json({"results": results, "total_count": total_count})


@app.put("/images/<image_id>")
async def replace_image(request: Request, image_id: str):
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
      - name: image_id
        description: The id of the image to be replaced.
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
    old_image_path = ""
    new_image_path = ""
    try:
        uploaded_file = request.files["image"][0]
        if not uploaded_file.type.startswith("image/"):
            return json(status=400)

        # Check if image exist in DB
        query = {"image_id": image_id}
        if not collection.count_documents(query):
            return response.json({"error": "Image not found"}, status=404)

        # # Retrieve image info from DB
        image_data = collection.find_one(query, {"_id": 0})
        image_id = image_data["image_id"]
        old_image_path = image_data["image_path"]
        image_data["info"].update({k: v[0] for k, v in dict(request.form).items()})

        try:
            # Save the new image file, overwriting the existing one
            _, file_extension = os.path.splitext(uploaded_file.name)
            new_image_path = str(
                IMAGE_DIRECTORY.joinpath(f"{image_id}{file_extension}")
            ).replace("\\", "/")

            with open(new_image_path, "wb") as f:
                f.write(uploaded_file.body)

            image_data["image_path"] = new_image_path

        except OSError as e:
            return response.json(
                {"error": f"Failed to replace image: {str(e)}"}, status=500
            )

        collection.replace_one(query, image_data)

    except KeyError:
        # Image file not provided
        if all(v == [""] for v in request.form.values()):
            return response.json({"message": "Nothing Changed"}, status=204)

    image_path = new_image_path or old_image_path
    return response.json(
        {
            "message": "Image replaced successfully",
            "image_id": image_id,
            "image_path": image_path,
        }
    )


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
      - name: details
        description: Return image info.
        in: path
        type: string
        required: false
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
        if request.args.get("details"):
            file_name, _ = os.path.splitext(image_name)
            query = {"image_id": file_name}
            if not collection.count_documents(query):
                return json({"error": "Image not found"}, status=404)

            image_data = collection.find_one(query, {"_id": 0})
            return json(image_data, status=404)

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
    app.run(host="0.0.0.0", port=9527)
