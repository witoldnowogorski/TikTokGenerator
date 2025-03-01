import ast
from pathlib import Path

from src.utils import BaseAgent, logger


VIDEO_IDEAS_PROMPT = """
I need help coming up with creative and engaging TikTok video ideas centered around a {TOPIC}.
 The videos should be unique, attention-grabbing, and tailored to resonate with the TikTok audience.

Your task is to brainstorm and outline five distinct questions which I can answer in my video, 
the questions must be interesting, not trivial,
 the answer to them must require presenting some interesting informations.
 
 Give me questions only, format them in python list where each string is separate question.
"""


IDEAS_EVALUATION_PROMPT = """
Here is the list of questions which i would like you to answer in my tiktok video.
Your task is to choose one whose answer will be interesting,
 engaging for viewers and will provide some interesting information.
 Format your output as a python list with one string (chosen question).
 
 Here is the list of questions: {QUESTIONS_LIST}
"""


SCRIPT_WRITING_PROMPT = """
You are an experienced content creator,
 you are working for a company which creates short (0.5-1.5 minute) videos for social platforms.

Your task is to write a script answering this question: {QUESTION} 

The script should capture the audience's attention from the start and delivers the key points in a concise way.

Here are steps for the script: 

Follow this guidelines:
- Start the script with a strong and relatable hook which captures attention.
- Script should be written in a concise, conversational style suitable for TikTok.
- Write script text only, DO NOT add timestamps, symbols (#, *, [, ]) or anything which might be improperly converted to audio.
- Scrip should have 100-200 words.
- End with a memorable closing statement or a preview of what's coming next.
- Provide a complete, clear, interesting and easy-to-understand answer to the question.
- Break down the explanation into manageable points or steps.
 
 Format your output as a python list with one string (script).
"""


TITLE_TAGS_PROMPT = """
I will give you a script for my TikTok video.
Your task is to generate title and 10 tags for this video. 
Format your output as a python list,
 where first element is the title and the remaining elements are the one word tags.
 
 Here is my script: {SCRIPT}
"""


class ScriptWriterAgent(BaseAgent):
    def generate(self, topic):
        ideas = self.generate_ideas(topic)
        logger.info("Generated ideas for a video: {}".format(ideas))

        idea = self.evaluate_ideas(ideas)
        logger.info("Chosen idea for a video: {}".format(idea))

        script = self.generate_script(idea)
        characters_to_drop = ["*", "<", ">", '"', "'"]
        for char in characters_to_drop:
            script = script.replace(char, "")
        logger.info("Generated script for a video: {}".format(script))

        title, tags = self.generate_title_and_tags(script)

        tags_processed = []
        for tag in tags:
            if not tag.startswith("#"):
                tags_processed.append("#" + tag)
            else:
                tags_processed.append(tag)

        logger.debug("Generated title and tags for a video: title: {}, tags: {}".format(title, tags_processed))

        return script, title, tags

    def generate_ideas(self, topic):
        prompt_contents = [VIDEO_IDEAS_PROMPT.format(TOPIC=topic)]
        res = self._inference(prompt_contents)
        return self._extract_content(res)

    def evaluate_ideas(self, ideas):
        prompt_contents = [IDEAS_EVALUATION_PROMPT.format(QUESTIONS_LIST=ideas)]
        res = self._inference(prompt_contents)
        return self._extract_content(res)

    def generate_script(self, idea):
        prompt_contents = [SCRIPT_WRITING_PROMPT.format(QUESTION=idea)]
        res = self._inference(prompt_contents)
        return self._extract_content(res)

    def generate_title_and_tags(self, script):
        prompt_contents = [TITLE_TAGS_PROMPT.format(SCRIPT=script)]
        res = self._inference(prompt_contents)
        res = res[res.find("["): res.find("]") + 1]
        logger.info("Generated title and tags for a video: {}".format(res))

        title_tags_list = ast.literal_eval(res)
        title = title_tags_list[0]
        tags = title_tags_list[1:]

        return title, tags

    @staticmethod
    def _extract_content(response):
        return response[response.find("[") + 1: response.find("]")]
