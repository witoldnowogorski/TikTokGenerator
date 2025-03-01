from pathlib import Path

from dotenv import load_dotenv

from src.base_videos_store.image_description_agent import ImageDescriptionAgent
from src.base_videos_store.utils import extract_first_frame, process_raw_videos

# RAW_VIDEOS_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/videos_raw"
# PROCESSED_VIDEOS_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/videos_processed"
# FIRST_FRAME_IMAGES_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/images"
# RAW_VIDEOS_PATH = "/data/videos_raw"
# PROCESSED_VIDEOS_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/videos_temp"
# FIRST_FRAME_IMAGES_PATH = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/data/images_temp"

DATA_PATH = Path("//data")


if __name__ == "__main__":
    ENV_PATH = "//config/.env"

    env_path = Path(ENV_PATH)
    load_dotenv(dotenv_path=env_path)

    # LOAD RAW VIDEOS

    process_raw_videos(DATA_PATH / "videos_raw", DATA_PATH / "videos_processed")

    # EXTRACT FIRST FRAME, RETURN DF
    df = extract_first_frame(DATA_PATH / "videos_processed", DATA_PATH / "images")

    image_description_agent = ImageDescriptionAgent()
    df = image_description_agent.generate(df)
    df.to_csv(DATA_PATH / "aviation.csv", index=False)
