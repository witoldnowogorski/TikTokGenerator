import os
import time
import logging
import functools
from abc import ABC, abstractmethod

from google import genai


def retry_on_exception(attempts=3, delay=1, backoff=5, exception=Exception):
    """
    A decorator to retry a function call if it raises a specified exception.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if attempt == attempts:
                        raise
                    else:
                        print(f"Attempt {attempt} failed: {e}. Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff

        return wrapper

    return decorator


class BaseAgent(ABC):
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = 'gemini-2.0-flash-001'

    @abstractmethod
    def generate(self, **kwargs):
        pass

    @retry_on_exception(attempts=3)
    def _inference(self, contents):
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents
        ).text

        return response


def setup_logger(name: str = "TikTokGenerator", log_file: str = "logs.txt", level: int = logging.INFO):
    """
    Sets up a logger with the specified name, log file, and level.
    Logs are written to both the console and the specified file.
    """
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger(level=logging.INFO)
