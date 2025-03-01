import os
from typing import List, Tuple

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ImageClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from src.video_generator.audio_transcriber import AudioTranscriber
from src.utils import logger


class VideoBuilder:
    def __init__(
        self,
        audio_path,
        video_paths,
        target_resolution=(500, 800),
        font_path = "/Users/wnowogorski/PycharmProjects/TikTokGenerator/assets/fonts/Roboto-VariableFont_wdth,wght.ttf",
        font_size = 25,
        subtitle_margin = 125,
        text_color: str = "white",
        bg_color: str = "red",
        max_words: int = 5,
        time_per_base_video: int = 8,
        output_path="generated_videos/full_video.mp4",
    ):
        self.audio_path = audio_path
        self.audio_clip = AudioFileClip(audio_path)
        self.duration = self.audio_clip.duration
        self.video_paths = video_paths
        self.target_resolution = target_resolution
        self.font_path = font_path
        self.font_size = font_size
        self.subtitle_margin = subtitle_margin
        self.text_color = text_color
        self.bg_color = bg_color
        self.max_words = max_words
        self.time_per_base_video = time_per_base_video

        self.output_path = output_path
        out_directory = os.path.dirname(output_path)
        if out_directory and not os.path.exists(out_directory):
            os.makedirs(out_directory)

        self.subtitles = None
        self.audio_transcriber = AudioTranscriber()

    def generate(self):
        logger.debug("Video Builder - Transcribing audio ... ")
        self.subtitles = self.audio_transcriber.transcribe_audio_with_timestamps(self.audio_path)

        logger.debug("Video Builder - Creating video ... ")
        base_video = self._create_video_from_videos()
        base_video = base_video.set_audio(self.audio_clip)
        logger.debug("")

        logger.debug("Video Builder - Adding subtitles ... ")
        subtitle_clips = self.create_subtitle_clips_from_transcription(self.subtitles)

        logger.debug("Video Builder - Saving video ...")
        final_video = CompositeVideoClip([base_video, *subtitle_clips], size=base_video.size)
        final_video.write_videofile(self.output_path, fps=24, codec="libx264", audio_codec="aac")
        base_video.close()
        self.audio_clip.close()

    def _resize_clip(self, clip: VideoFileClip) -> VideoFileClip:
        """
        Resize the clip to fit the target resolution while preserving aspect ratio.
        Adds black letterboxing as needed.
        """
        target_w, target_h = self.target_resolution
        clip_w, clip_h = clip.size
        scale = min(target_w / clip_w, target_h / clip_h)
        clip_resized = clip.resize(scale)
        clip_with_bg = clip_resized.on_color(
            size=self.target_resolution,
            color=(0, 0, 0),
            pos="center"
        )
        return clip_with_bg

    def _create_video_from_videos(self) -> VideoFileClip:
        """
        Load each video, resize them, and concatenate into one clip.
        """
        clips = []
        for path in self.video_paths:
            clip = VideoFileClip(path)
            clip = self._resize_clip(clip)
            clip = clip.set_duration(self.time_per_base_video)
            clips.append(clip)
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.set_duration(self.duration)
        return final_clip

    def _create_subtitle_clips(self) -> List[ImageClip]:
        """
        Split the provided script into segments (each with max_words words).
        Create an ImageClip for each segment, each lasting for a fraction
        of the audio's duration. The clips are positioned near the bottom.
        """
        # Split the script into words and then group them
        words = self.script.split()
        subtitle_segments = [
            " ".join(words[i : i + self.max_words])
            for i in range(0, len(words), self.max_words)
        ]
        num_segments = len(subtitle_segments)
        # Calculate duration per subtitle segment
        seg_duration = self.duration / num_segments if num_segments > 0 else self.duration

        subtitle_clips = []
        for idx, text in enumerate(subtitle_segments):
            # Create an image with the subtitle text on a red rounded rectangle
            subtitle_img = self._create_subtitle_image(text)
            # Create an ImageClip from the numpy array
            clip = ImageClip(np.array(subtitle_img), transparent=True)
            clip = clip.set_duration(seg_duration)
            clip = clip.set_start(idx * seg_duration)
            # Position at bottom center with a margin upward
            clip = clip.set_position(("center", self.target_resolution[1] - clip.h - self.subtitle_margin))
            subtitle_clips.append(clip)
        return subtitle_clips

    def _create_subtitle_image(self, text: str, padding: int = 15, radius: int = 15) -> Image:
        """
        Create a PIL image with the subtitle text rendered on top of a
        rounded rectangle with a red background. The text is centered.
        If the text exceeds the width, it will be split into multiple lines.
        """
        font = ImageFont.truetype(self.font_path, self.font_size)
        max_width = self.target_resolution[0] - 2 * padding  # Max width available for the subtitle

        # Split the text into lines based on the max width
        words = text.split()
        lines = []
        current_line = []

        # Loop over each word and check if adding it would exceed the max width
        for word in words:
            line_width = font.getbbox(" ".join(current_line + [word]))[2] - font.getbbox(" ".join(current_line))[0]
            if line_width <= max_width:
                current_line.append(word)
            else:
                # When the line exceeds the max width, push the current line to the lines list
                lines.append(" ".join(current_line))
                current_line = [word]  # Start a new line with the current word

        # Add the last line if any
        if current_line:
            lines.append(" ".join(current_line))

        # Calculate the final text width and height
        text_w = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
        text_h = sum([font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines])

        # Define image size with padding and enough height to fit multiple lines
        img_w = text_w + 2 * padding
        img_h = text_h + 2 * padding + 10

        # Ensure the background height doesn't exceed the video frame
        img_h = min(img_h, self.target_resolution[1] - 2 * self.subtitle_margin)

        # Create an image with transparent background (RGBA)
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw a rounded rectangle (background)
        rect_coords = (0, 0, img_w, img_h)
        draw.rounded_rectangle(
            rect_coords,
            radius=radius,
            fill=self.bg_color
        )

        # Draw the text centered
        y_offset = (img_h - text_h) / 2  # Start from the top part of the background
        for line in lines:
            line_w = font.getbbox(line)[2] - font.getbbox(line)[0]
            text_x = (img_w - line_w) / 2  # Center the text horizontally
            draw.text((text_x, y_offset), line, font=font, fill=self.text_color)
            y_offset += font.getbbox(line)[3] - font.getbbox(line)[1]  # Move down for the next line

        return img


    def create_subtitle_clips_from_transcription(self, subtitles, max_words_per_subtitle=5):
        subtitle_clips = []
        num_segments = len(subtitles) // max_words_per_subtitle
        for i in range(num_segments):
            # Get the words for this subtitle segment
            segment = subtitles[i * max_words_per_subtitle: (i + 1) * max_words_per_subtitle]
            text = " ".join([word["word"] for word in segment])

            # Use the first word's start time and the last word's end time for the timing
            start_time = segment[0]["start"]
            end_time = segment[-1]["end"]

            # Create the subtitle image as you already do
            subtitle_img = self._create_subtitle_image(text)
            clip = ImageClip(np.array(subtitle_img), transparent=True)
            clip = clip.set_start(start_time).set_end(end_time)

            # Position the subtitle at the bottom of the screen
            clip = clip.set_position(("center", self.target_resolution[1] - clip.h - self.subtitle_margin))
            subtitle_clips.append(clip)

        return subtitle_clips



