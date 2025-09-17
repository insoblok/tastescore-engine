import requests
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class Utils:
    def __init__(self):
        self.session = requests.session()
    
    def load_response(self, path: str, method="get", params={}):
        """Load response from Blockchain.info API"""
        try:
            if method == "get":
                response = self.session.get(path)
            elif method == "post":
                response = self.session.post(path, json=params);
            response.raise_for_status()
            
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON: {e}")
