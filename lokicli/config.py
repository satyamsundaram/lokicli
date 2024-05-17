#!/usr/bin/env python3

import os
import logging
import configparser

class LokiConfig:
    def __init__(self):
        self.CONFIG_FILE = self.get_file_path('lokicli.conf')

    def get_properties(self):
        try:
            self.write_properties_file()
            with open(self.get_file_path('properties.ini'), 'r') as f:
                properties = configparser.ConfigParser()
                properties.read_file(f)
                return properties
        except Exception as e:
            logging.error(f"Error getting Loki properties file: {e}")
            raise e

    def write_properties_file(self):
        try:
            propertiesFilePath = self.get_file_path('properties.ini')
            config = configparser.ConfigParser()
            config.add_section('logReader')
            config.set('logReader', 'batchSize', '250')
            config.set('logReader', 'defaultLimit', '1000')

            config.add_section('validProjects')
            config.set('validProjects', 'projects', 's2s, ao3, s2s-use1')

            with open(propertiesFilePath, 'w') as f:
                config.write(f)
        except Exception as e:
            logging.error(f"Error writing Loki properties file: {e}")
            raise e

    @staticmethod
    def get_file_path(filename):
        try:
            if os.name == 'nt':
                lokicli_dir = os.path.join("C:" + os.sep, ".lokicli")
            else:
                home_dir = os.path.expanduser("~")
                lokicli_dir = os.path.join(home_dir, '.lokicli')
            os.makedirs(lokicli_dir, exist_ok=True)
            return os.path.join(lokicli_dir, filename)
        except Exception as e:
            logging.error(f"Error getting file path: {e}")
            print(f"Error getting file path: {e}")

    def load_project(self):
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, "r") as file:
                    return file.read().strip()
            else:
                return ""
        except Exception as e:
            logging.error(f"Error loading Loki project: {e}")
            print(f"Error loading Loki project: {e}")

    def save_project(self, project):
        try:
            with open(self.CONFIG_FILE, "w") as file:
                file.write(project)
        except Exception as e:
            logging.error(f"Error saving Loki project: {e}")
            raise e
