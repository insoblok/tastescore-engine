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
    
    def load_response(self, path: str):
        """Load response from Blockchain.info API"""
        try:
            response = self.session.get(path)
            response.raise_for_status()
            
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON: {e}")
