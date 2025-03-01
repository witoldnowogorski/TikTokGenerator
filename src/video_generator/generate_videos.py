import os
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from moviepy.audio.io.AudioFileClip import AudioFileClip

from src.utils import logger
from src.video_generator.script_writer_agent import ScriptWriterAgent
from src.video_generator.vector_store import VectorStore
from src.video_generator.videos_finder_agent import VideoFinderAgent
from src.video_generator.audio_generation_agent import AudioGenerationAgent
from src.video_generator.video_builder import VideoBuilder
from src.uploaders.yt_upload import authenticate_youtube, upload_shorts

ENV_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/config/.env"


def generate(topic, num_videos, time_per_base_video=7, drop_vs_if_exists=False):
    env_path = Path(ENV_PATH)
    load_dotenv(dotenv_path=env_path)

    youtube = authenticate_youtube()

    vector_store = VectorStore()
    # if drop_vs_if_exists and Path(":memory:").exists():
    #     logger.info(f"Removing existing vector store")
    #     shutil.rmtree(":memory:")
    # df = pd.read_csv(f"/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/descriptions/{topic}.csv")
    # vector_store.store(df)

    for video_num in range(num_videos):
        try:
            script_writer = ScriptWriterAgent()
            script, title, tags = script_writer.generate(topic)

            audio_generation = AudioGenerationAgent()
            audio_path = audio_generation.generate(script)
            audio_clip_duration = AudioFileClip(audio_path).duration

            vf = VideoFinderAgent()
            num_videos = int((audio_clip_duration // time_per_base_video) + 2)
            video_paths = vf.generate(script, vector_store, num_videos)

            video_output_path = f"generated_videos/video_{video_num}.mp4"
            video_builder = VideoBuilder(
                audio_path,
                video_paths,
                output_path=video_output_path,
                time_per_base_video=time_per_base_video
            )
            video_builder.generate()

            logger.info(
                f"VIDEO GENERATION COMPLETE: {video_num} / {num_videos} \n"
                f"Path: {video_output_path} \n"
                f"Title: {title} \n"
                f"Tags: {tags}\n"
            )

            video_id = upload_shorts(youtube, video_output_path, title, tags, topic)
            logger.info(f"Video is uploaded: https://www.youtube.com/watch?v={video_id}")

        except Exception as e:
            logger.error("An error occurred during the generation: {}".format(e))

generate("Aviation", 30, time_per_base_video=7)