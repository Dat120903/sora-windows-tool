import time
import random
import uuid

class MockSoraClient:
    def __init__(self, failure_rate=0.0):
        self.failure_rate = failure_rate
        self.jobs = {}

    def create_video(self, account_cookie: str, prompt: str) -> str:
        self._simulate_network()
        if self.failure_rate > 0 and random.random() < self.failure_rate:
            if random.random() < 0.5:
                raise Exception("429 Too Many Requests")
            else:
                raise Exception("401 Unauthorized")
        video_id = f"sora_{uuid.uuid4().hex[:8]}"
        self.jobs[video_id] = {"status": "processing", "created_at": time.time()}
        return video_id

    def get_status(self, video_id: str) -> str:
        self._simulate_network()
        if video_id not in self.jobs:
            raise Exception("404 Not Found")
        job = self.jobs[video_id]
        if time.time() - job['created_at'] > 3:
            job['status'] = "finished"
        return job['status']

    def download_video(self, video_id: str, path: str):
        self._simulate_network()
        if self.jobs.get(video_id, {}).get('status') != "finished":
            raise Exception("Video not ready")
        with open(path, 'w') as f:
            f.write(f"Mock video content for {video_id}")

    def _simulate_network(self):
        time.sleep(0.05)
