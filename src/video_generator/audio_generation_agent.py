import os

from google.cloud import texttospeech

from src.utils import BaseAgent


class AudioGenerationAgent(BaseAgent):
    def __init__(self, output_dir="temp/output_audio.wav"):
        super().__init__()
        self.output_dir = output_dir
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp-HD-F"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

    def generate(self, text) -> str:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )

        out_directory = "/".join(self.output_dir.split("/")[:-1])
        if not os.path.exists(out_directory) and out_directory != "":
            os.makedirs(out_directory)

        with open(self.output_dir, "wb") as out:
            out.write(response.audio_content)

        return self.output_dir
