from pathlib import Path

from src.utils import BaseAgent


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
 you are working for a company which creates short (1-2 minutes) videos for social platforms.

Your task is to write a script answering this question: {QUESTION} 

The script should capture the audience's attention from the start and delivers the key points in a concise way.

Here are steps for the script: 

Follow this guidelines:
- Start the script with a strong and relatable hook which captures attention.
- Script should be written in a concise, conversational style suitable for TikTok.
- Write script text only, DO NOT add timestamps, symbols (#, *, [, ]) or anything which might be improperly converted to audio.
- Scrip should have 200-300 words.
- End with a memorable closing statement or a preview of what's coming next.
- Provide a complete, clear, interesting and easy-to-understand answer to the question.
- Break down the explanation into manageable points or steps.
 
 Format your output as a python list with one string (script).
"""


class ScriptWriterAgent(BaseAgent):
    def generate(self, topic):
        ideas = self.generate_ideas(topic)
        idea = self.evaluate_ideas(ideas)
        script = self.generate_script(idea)

        characters_to_drop = ["*", "<", ">"]
        for char in characters_to_drop:
            script = script.replace(char, "")

        return script

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

    @staticmethod
    def _extract_content(response):
        return response[response.find("[") + 1: response.find("]")]
