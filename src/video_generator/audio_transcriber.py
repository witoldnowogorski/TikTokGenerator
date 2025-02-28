import io
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech


class AudioTranscriber:
    def __init__(self, chunk_length_ms=30000):  # 60 seconds chunks by default
        self.chunk_length_ms = chunk_length_ms
        self.client = speech.SpeechClient()

    def split_audio(self, audio_path):
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)
        # Split the audio into chunks based on chunk_length_ms
        chunks = []
        for start_ms in range(0, len(audio), self.chunk_length_ms):
            chunk = audio[start_ms:start_ms + self.chunk_length_ms]
            chunks.append(chunk)
        return chunks

    def transcribe_audio_chunk(self, chunk):
        # Save chunk as a temporary file
        temp_audio_path = "temp_audio.wav"
        chunk.export(temp_audio_path, format="wav")

        with io.open(temp_audio_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US",
            enable_word_time_offsets=True,
        )

        # Send the request for transcription
        response = self.client.recognize(config=config, audio=audio)

        # Process the response and extract word-level timestamps
        subtitles = []
        for result in response.results:
            for alternative in result.alternatives:
                for word_info in alternative.words:
                    start_time = word_info.start_time.total_seconds()
                    end_time = word_info.end_time.total_seconds()
                    word = word_info.word
                    subtitles.append({"word": word, "start": start_time, "end": end_time})

        return subtitles

    def combine_subtitles(self, subtitles_chunks):
        all_subtitles = []
        offset = 0  # Track time offset between chunks

        for chunk_subtitles in subtitles_chunks:
            for subtitle in chunk_subtitles:
                subtitle["start"] += offset
                subtitle["end"] += offset
                all_subtitles.append(subtitle)

            # Update the offset for the next chunk
            if chunk_subtitles:
                last_chunk_end = chunk_subtitles[-1]["end"]
                offset = last_chunk_end  # Set the new offset for the next chunk

        return all_subtitles

    def transcribe_audio_with_timestamps(self, audio_path):
        # Step 1: Split the audio into smaller chunks
        chunks = self.split_audio(audio_path)

        # Step 2: Transcribe each chunk
        subtitles_chunks = []
        for chunk in chunks:
            chunk_subtitles = self.transcribe_audio_chunk(chunk)
            subtitles_chunks.append(chunk_subtitles)

        # Step 3: Combine all the subtitles and synchronize the timestamps
        final_subtitles = self.combine_subtitles(subtitles_chunks)

        return final_subtitles
