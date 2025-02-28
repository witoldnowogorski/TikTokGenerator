import os
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.video_generator.script_writer_agent import ScriptWriterAgent
from src.video_generator.vector_store import VectorStore
from src.video_generator.videos_finder_agent import VideoFinderAgent
from src.video_generator.audio_generation_agent import AudioGenerationAgent
from src.video_generator.video_builder import VideoBuilder

ENV_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/config/.env"

def generate(topic):
    env_path = Path(ENV_PATH)
    load_dotenv(dotenv_path=env_path)

    df = pd.read_csv("/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/descriptions.csv")

    script_writer = ScriptWriterAgent()
    script = script_writer.generate(topic)

    if Path(":memory:").exists():
        shutil.rmtree(":memory:")

    vector_store = VectorStore()
    vector_store.store(df)

    vf = VideoFinderAgent()
    video_paths = vf.generate(script, vector_store)

    audio_generation = AudioGenerationAgent()
    audio_path = audio_generation.generate(script)

    video_builder = VideoBuilder(
        audio_path,
        video_paths,
        output_path="generated_videos/full.mp4"
    )
    video_builder.generate()

    # shutil.rmtree("temp")

generate("AVIATION")