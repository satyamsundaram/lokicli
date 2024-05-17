#!/usr/bin/env python3

import requests
import json
import logging
import configparser

from .time_utils import LokiTimeUtils
from .app_map_utils import AppMapUtils
from .config import LokiConfig
from .auth import Auth

class LogReader:
    def __init__(self, project, url):
        self.logs = []
        self.project = project
        self.url = url

        try:
            properties = LokiConfig().get_properties()
            self.batch_size = int(properties['logReader']['batchSize'])
        except Exception as e:
            logging.error(f"Error getting batch size: {e}")
            raise e

    def _get_log_query(self, app_name, regex_query, invert_match):
        try:
            app, namespace, instance = app_name["app"], app_name["namespace"], app_name["instance"]
            query = f'{{app="{app}",namespace="{namespace}",instance="{instance}"}}'
            operator = ' !~ `' if invert_match else ' |~ `'
            query = query + operator + regex_query + '`' if regex_query else query
            return query
        except Exception as e:
            logging.error(f"Error getting query: {e}")
            raise e

    def build_params(self, start_time, current_end_time, limit, query):
        return {
            "direction": "BACKWARD",
            "end": current_end_time,
            "limit": limit if limit < self.batch_size else self.batch_size,
            "query": query,
            "start": start_time,
        }

    def fetch_logs(self, params, access_token):
        try:
            cookies = {"_oauth2_proxy": access_token}
            response = requests.get(f"{self.url}/loki/api/v1/query_range", cookies=cookies, params=params, timeout=60)

            if response.status_code != 200:
                logging.error(f"Error fetching logs: {response.status_code}. Response: {response.text}")
                if 'parse error' in response.text:
                    raise Exception(f"Error fetching logs: {response.status_code}. Please ensure the regex query is according to the Google RE2 syntax. {response.text}")
                else:
                    raise Exception(f"Error fetching logs: {response.status_code}. Response: {response.text}")
            
            result = response.json()["data"]["result"]
            self.logs = []
            
            if len(result):
                log_values = result[0]["values"]
                for item in log_values:
                    self.logs.append({"log":json.loads(item[1])["log"], "timestamp": item[0]})
        except KeyboardInterrupt:
            logging.error("Interrupted by user.")
            raise KeyboardInterrupt
        except Exception as e:
            logging.error(f"Error fetching logs: {e}")
            raise e

        return self.logs

    def get_processed_params(self, app_name, limit, from_time, to_time, since, regex_query, invert_match, access_token, context):
        try:
            if limit > 500000:
                logging.error("Limit cannot be greater than 500000.")
                raise ValueError("Limit cannot be greater than 500000.")

            from_time, to_time = LokiTimeUtils().get_from_and_to_times(from_time, to_time, since)
            start_time = LokiTimeUtils.utc_to_unix_nanosecond_epoch(from_time)
            end_time = LokiTimeUtils.utc_to_unix_nanosecond_epoch(to_time)
            app_map = AppMapUtils(self.url, self.project).get_app_map(from_time, to_time, access_token)

            if app_name not in app_map:
                logging.error(f"No logs found for {app_name} in {self.project} project for the specified time range.")
                raise ValueError(f"No logs found for {app_name} in {self.project} project for the specified time range. Please check the app name, project and time range.")

            query = self._get_log_query(app_map[app_name], regex_query, invert_match)

            if context:
                if not regex_query:
                    logging.error("Context can only be used for a query.")
                    raise ValueError("Context can only be used for a query.")

                if context > 250:
                    logging.error("Context cannot be greater than 250.")
                    raise ValueError("Context cannot be greater than 250.")
        except Exception as e:
            logging.error(f"Error getting processed params: {e}")
            raise e

        return start_time, end_time, limit, query
