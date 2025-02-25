import time
import random
from concurrent.futures import ThreadPoolExecutor

class SingletonModel:
    _instance = None
    _executor = ThreadPoolExecutor(max_workers=1) # Single worker to serialize model access

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def predict(self, data: dict) -> dict:
        delay = random.uniform(10, 40)  # This line is to simulate model inference
        time.sleep(delay)
        return {"answer": "Dude this is Deep Seek, not Deep Thought."}