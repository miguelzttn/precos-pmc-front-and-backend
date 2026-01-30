import os
import time
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class APIClient:

    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/v1/frontend")
    API_KEY = os.getenv("API_SECRET_KEY", "teste")

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.API_BASE_URL
        self.headers = {"X-API-KEY": self.API_KEY}

    def get(self, endpoint, params=None):
        start_time = time.time()
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        print(f"GET {endpoint} took {(time.time() - start_time):.2f} seconds")
        return response.json()

    def post(self, endpoint, data=None):
        start_time = time.time()
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        print(f"POST {endpoint} took {(time.time() - start_time):.2f} seconds")
        return response.json()

    def put(self, endpoint, data=None, params=None):
        start_time = time.time()
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, headers=self.headers, json=data, params=params)
        response.raise_for_status()
        print(f"PUT {endpoint} took {(time.time() - start_time):.2f} seconds")
        return response.json()


backend = APIClient()
