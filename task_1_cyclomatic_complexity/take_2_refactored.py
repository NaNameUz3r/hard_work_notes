import os
import argparse
import aiohttp
import glob
import asyncio

class ImageUploader:
    def __init__(self,
                 image_dir,
                 csv_name,
                 csv_delimiter,
                 api_url,
                 request_timeout,
                 max_concurrent_uploads) -> None:
        self.image_dir = image_dir
        self.csv_name = csv_name
        self.csv_delimiter = csv_delimiter
        self.api_url = api_url
        self.request_timeout = request_timeout
        self.max_concurrent_uploads = max_concurrent_uploads

    async def upload_image(self, session, image_path):
        try:
            async with session.post(self.api_url, data={'file': open(file=image_path, mode='rb')}, timeout=self.request_timeout) as response:
                await self.handle_upload_response(response, image_path)
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            self.handle_upload_error(image_path, e)

    async def process_images(self):
        if not os.path.exists(self.image_dir):
            print(f"Error: '{self.image_dir}' directory not found.")
            return

        images = glob.glob(os.path.join(self.image_dir, "*"))

        async with aiohttp.ClientSession() as session:
            tasks = [self.upload_image(session, image_path) for image_path in images]
            await asyncio.gather(*tasks)

    async def handle_upload_response(self, response, image_path):
        if response.status == 201:
            data = await response.json()
            image_id = data.get("ID")
            print(f"Uploaded '{image_path}' with ID: {image_id}")
            return image_path, image_id
        print(f"Failed to upload '{image_path}'. Status code: {response.status}")

    def handle_upload_error(self, image_path, error) -> None:
        if isinstance(error, asyncio.TimeoutError):
            print(f"Request for '{image_path}' timed out.")
        if isinstance(error, aiohttp.ClientError):
            print(f"Error occurred while uploading '{image_path}': {error}")

def parse_args():
    parser = argparse.ArgumentParser(description="""Upload images to fastAPI-img-store and
                                     generate CSV with image paths and uploaded image IDs.""")
    parser.add_argument("--image_dir",
                        type=str,
                        required=True,
                        help="Path to the directory with images.")
    parser.add_argument("--csv_name",
                        type=str,
                        default="uploaded_images.csv",
                        help="Name of the CSV file.")
    parser.add_argument("--csv_delimiter",
                        type=str,
                        default=";",
                        help="Delimiter for the CSV file.")
    parser.add_argument("--api_url",
                        type=str,
                        default="http://127.0.0.1:8000/images/",
                        help="Server API URL.")
    parser.add_argument("--request_timeout",
                        type=int,
                        default=30,
                        help="Timeout for API requests in seconds.")
    parser.add_argument("--max_concurrent_uploads",
                        type=int,
                        default=5,
                        help="Maximum number of concurrent uploads.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    uploader = ImageUploader(image_dir=args.image_dir,
                             csv_name=args.csv_name,
                             csv_delimiter=args.csv_delimiter,
                             api_url=args.api_url,
                             request_timeout=args.request_timeout,
                             max_concurrent_uploads=args.max_concurrent_uploads)
    asyncio.run(uploader.process_images())

if __name__ == "__main__":
    main()
