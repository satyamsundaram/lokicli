#!usr/bin/env python3

from datetime import datetime, timezone
import requests
import logging
from .auth import Auth

class AppMapUtils:
    def __init__(self, url, project):
        self.url = url
        self.project = project
        self.app_map = {}

    def _populate_app_map(self, labels):
        try:
            for label in labels:
                if 'app' in label and 'instance' in label and 'namespace' in label:
                    namespace = label['namespace']
                    new_label = f"{label['app']}-{label['instance']}-"
                    new_label += 'prod' if namespace == 'production' else 'stage' if namespace == 'staging' else namespace
                    self.app_map[new_label] = label
        except Exception as e:
            logging.error(f"Error populating app map: {e}")
            raise e

    def get_app_map(self, from_time, to_time, access_token):
        params = {
            "end": to_time,
            "match": "{}",
            "start": from_time,
        }

        try:
            cookies = {"_oauth2_proxy": access_token}
            response = requests.get(f"{self.url}/loki/api/v1/series", cookies=cookies, params=params, timeout=60)
            if response.status_code == 400:
               logging.error("Selected time range is out of range. Valid time range is within last 720 hours.")
               raise Exception("Selected time range is out of range. Valid time range is within last 720 hours.")
            if response.status_code != 200:
                logging.error(f"Error getting app map: {response.status_code}, {response.text}")
                raise Exception(f"Error getting app map: {response.status_code}, {response.text}")
            labels = response.json()["data"]
            self._populate_app_map(labels)
        except KeyboardInterrupt:
            logging.error("Interrupted by user.")
            raise KeyboardInterrupt
        except Exception as e:
            logging.error(f"Error getting app map: {e}")
            raise e

        return self.app_map
