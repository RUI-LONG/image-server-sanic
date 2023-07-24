import os
import unittest
import requests

# Replace with the URL of your API endpoint
API_ENDPOINT = "http://localhost:8000/image/upload"

# Replace with the path to the folder containing the test images
IMAGE_FOLDER = "../test_images"


class TestImageUpload(unittest.TestCase):
    def test_upload_images(self):
        # Get a list of all image files in the folder
        image_files = [
            os.path.join(IMAGE_FOLDER, f)
            for f in os.listdir(IMAGE_FOLDER)
            if os.path.isfile(os.path.join(IMAGE_FOLDER, f))
        ]

        for file_path in image_files:
            with open(file_path, "rb") as file:
                _, file_extension = os.path.splitext(file_path)
                file_type = f"image/{file_extension.strip('.')}"
                files = [("image", (file.name, file, file_type))]
                response = requests.post(API_ENDPOINT, files=files)

            self.assertEqual(response.status_code, 200)
            self.assertIn("message", response.json())

            print(f"Uploaded file: {file_path}")
            print(f"Response: {response.json()}")
            print("-" * 30)


if __name__ == "__main__":
    unittest.main()
