import os
import pandas as pd
from moviepy.editor import VideoFileClip

def extract_first_frame(video_dir, image_dir):
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    records = []

    for filename in os.listdir(video_dir):
        if filename.lower().endswith(".mp4"):
            video_path = os.path.join(video_dir, filename)

            clip = VideoFileClip(video_path)

            image_filename = os.path.splitext(filename)[0] + ".png"
            image_path = os.path.join(image_dir, image_filename)

            clip.save_frame(image_path, t=0)

            records.append({
                "video_path": video_path,
                "image_path": image_path
            })

            clip.close()

    df = pd.DataFrame(records)
    return df


def crop_to_phone(clip, target_ratio=9/16):
    """
    Crop the clip to the center with the given target aspect ratio (default 9:16).
    """
    original_w, original_h = clip.size
    original_ratio = original_w / original_h

    # If the video is too wide compared to 9:16, crop the width.
    if original_ratio > target_ratio:
        new_w = original_h * target_ratio
        x1 = (original_w - new_w) / 2
        x2 = x1 + new_w
        cropped = clip.crop(x1=x1, x2=x2)
    # If the video is too tall, crop the height.
    else:
        new_h = original_w / target_ratio
        y1 = (original_h - new_h) / 2
        y2 = y1 + new_h
        cropped = clip.crop(y1=y1, y2=y2)

    return cropped


def process_raw_videos(input_dir, output_dir, segment_duration=10, num_segments=1):
    """
    Processes each mp4 file in input_dir: crops to 9:16, splits into segments,
    and writes segments to output_dir.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mp4"):
            input_path = os.path.join(input_dir, filename)
            print(f"Processing {input_path}...")
            clip = VideoFileClip(input_path)

            # Crop the clip to phone aspect ratio
            cropped_clip = crop_to_phone(clip)

            base_filename = os.path.splitext(filename)[0]

            for i in range(num_segments):
                start = i * segment_duration
                end = start + segment_duration
                if end > cropped_clip.duration:
                    end = cropped_clip.duration
                segment = cropped_clip.subclip(start, end)
                output_filename = f"{base_filename}_part{i+1}.mp4"
                output_path = os.path.join(output_dir, output_filename)
                print(f"  Writing segment {i+1} to {output_path}...")
                segment.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

            # Clean up
            clip.close()
            cropped_clip.close()
