import ast

from src.utils import BaseAgent, logger


SCRIPT = """
Ever stuck your hand out the car window and felt it lift? Okay, now forget everything you think you know about why airplanes fly.
Most people think airplanes fly because the air rushing over the curved top of the wing has further to travel, so it has to speed up, creating lower pressure and sucking the wing upwards. Right? WRONG!
That’s a HUGE oversimplification. Here’s the surprising truth: it's mostly about *deflection*.
Think of the wing like a ramp. As the wing moves through the air, it forces the air *downwards*. This downward push creates an equal and opposite reaction – the air pushes the wing *upwards*! That's lift, baby!
It’s Newton's third law in action: for every action, there's an equal and opposite reaction. The wing pushes air down, the air pushes the wing up.
While the curved wing *does* play a role in creating a pressure difference, the primary force lifting a plane is the downward deflection of air. Planes with symmetrical wings can even fly upside down! How? By angling the wing to deflect air downwards.
So, next time you see a plane, remember it's not just slicing through the air, it’s actively pushing it down to soar!
Mind blown? Let me know if you want more airplane facts!
"""

DESCRIBE_SUITABLE_VIDEO_PROMPT = """
You will be provided with a script for a short TikTok video.  
Your task is to describe three ideas for the most suitable image to display for each segment of the script as it is being read.  

Generate 3 distinct ideas for an image for each of {NUM_VIDEOS} segments of the video,
 ensuring that the first image is best suited for the opening and the last image is most appropriate for the closing.
Format your output as a python list of sets, where each set contains three strings (three distinct ideas for an image).

Ideas for one segment must differ from each other, they can't be similar.

Here is script: {SCRIPT}
"""


class VideoFinderAgent(BaseAgent):
    def generate(self, script, vector_store, num_videos):
        logger.debug(f"Looking for {num_videos} videos ...")
        prompt_content = [DESCRIBE_SUITABLE_VIDEO_PROMPT.format(NUM_VIDEOS=num_videos, SCRIPT=script)]
        response = self._inference(prompt_content)

        descriptions = self._extract_content(response)

        paths = []
        for i, descs in enumerate(descriptions):
            min_distance = 1000
            best_match = None
            for desc in descs:
                vs_res = vector_store.query(desc, k=1)
                distance = vs_res["distances"][0][0]
                match = vs_res["metadatas"][0][0]
                if distance < min_distance and match not in paths:
                    min_distance = distance
                    best_match = match

            logger.debug(f"Searching for a most suitable video: {i} / {num_videos}, Best match: {best_match}")
            paths.append(best_match)

        return [v["path"] for v in paths]

    @staticmethod
    def _extract_content(response):
        desc_list = response[response.find("["): response.find("]") + 1]
        desc_list = desc_list.replace("'", "")
        descriptions = ast.literal_eval(desc_list)
        return descriptions
