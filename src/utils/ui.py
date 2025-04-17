import base64


class UserInterfaceUtils:
    def get_image_base64(self, image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
