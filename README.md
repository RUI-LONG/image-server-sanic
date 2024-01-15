# Image Server

This is an image server designed specifically for photos CRUD operations, and operates as the website's backend: [神龍變裝](https://www.wuwish.com.tw/)

[API Blueprint](https://rui-long.github.io/image-server-sanic/)

## Usage

Before running the Sanic Image Server, please ensure that you have the following prerequisites installed on your system:

- Python 3.8
- Sanic

### Installation

To install and set up the Sanic Image Server, follow these steps:

1. **Step 1:** Clone the project code to your local machine using Git:

   ```
   git clone https://github.com/RUI-LONG/image-server
   cd image-server
   ```

2. **Step 2:** Install the required dependencies. It is recommended to use a virtual environment:
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Step 3: Start the Sanic Image Server:
    ```
    python app.py
    ```

## Supported Image Formats

This image server supports the following common image formats:

| Image Format        | Supported |
| ------------        | --------- |
| JPEG (.jpg, .jpeg)  | ✔️        |
| PNG (.png)          | ✔️        |
| GIF (.gif)          | ✔️        |
| WebP (.webp)        | ✔️        |
| AVIF (.avif)        | ❌        |
| SVG (.svg)          | ❌        |
| BMP (.bmp)          | ✔️        |

## Contribution

If you encounter any issues or have suggestions for improvements, please feel free to submit an issue or pull request to help enhance this project.

## License

[Specify your project's license here, e.g., MIT License]

Thank you for using our Cosplay Image Server! We look forward to seeing your amazing cosplay creations!
