import time
import random
from concurrent.futures import ThreadPoolExecutor

class SingletonModel:
    _instance = None
    _executor = ThreadPoolExecutor(max_workers=1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def predict_async(self, data: dict) -> asyncio.Future:
        """Submit prediction task to executor and return Future"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(
            self._executor, 
            self._blocking_predict, 
            data
        )

    def _blocking_predict(self, data: dict) -> dict:
        delay = random.uniform(10, 40)
        time.sleep(delay)
        return {"answer": "..."}
