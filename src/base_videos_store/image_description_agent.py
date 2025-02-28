from src.utils import BaseAgent, retry_on_exception


IMAGE_DESCRIPTION_PROMPT = """
Could you describe this image? Format your output as a python list with one string
"""


class ImageDescriptionAgent(BaseAgent):
    def generate(self, images_df):
        descriptions = []
        for i, image_path in enumerate(images_df['image_path']):
            print("Describing images: {}/{}".format(i, len(images_df)))
            des = self.get_description_text(image_path)
            image_description = des[des.find('[') + 1:des.find(']')]
            descriptions.append(image_description)

        images_df['description'] = descriptions

        return images_df

    @retry_on_exception(attempts=2)
    def get_description_text(self, image_path):
        file = self.client.files.upload(file=image_path)
        prompt_contents = [IMAGE_DESCRIPTION_PROMPT, file]
        response = self._inference(prompt_contents)

        return response
