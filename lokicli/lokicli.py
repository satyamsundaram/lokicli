#!/usr/bin/env python3

import requests
import argparse
import logging
import re
import colorama
from datetime import datetime, timezone

from .subparsers import Subparsers
from .config import LokiConfig
from .time_utils import LokiTimeUtils
from .app_map_utils import AppMapUtils
from .log_reader import LogReader
from .auth import Auth
from .contextual_logs import ContextualLogs

class LokiCLI:
    def __init__(self):
        self.lokiConfig = LokiConfig()
        self.project = self.lokiConfig.load_project()
        self.url = f"https://loki-gateway.{self.project}.{self.lokiConfig.get_properties()['urlSuffix']}"
        self.auth = Auth(self.url)
        self.version = "1.1.1"

        try:
            properties = self.lokiConfig.get_properties()
            self.valid_projects = properties['validProjects']['projects'].split(", ")
        except Exception as e:
            logging.error(f"Error getting Loki properties file: {e}")
            raise e

    def _check_project(self, project):
        if not self.project and not project:
            logging.error("Project not set.")
            raise Exception("Error: Project not set.")
        if project:
            self.set_project(project)

    def set_project(self, project):
        valid_projects = self.valid_projects
        try:
            if project in valid_projects:
                self.project = project
                self.url = f"https://loki-gateway.{project}.{self.lokiConfig.get_properties()['urlSuffix']}"
                self.lokiConfig.save_project(project)
            else:
                raise ValueError(f"Invalid project: {project}")
        except Exception as e:
            logging.error(f"Error setting Loki project: {e}")
            raise e

    def list_apps(self, from_time, to_time, since, project):
        try:
            self._check_project(project)
            self.login(project)
            access_token = self.auth.get_saved_access_token(self.project)
            
            from_time, to_time = LokiTimeUtils().get_from_and_to_times(from_time, to_time, since)
            app_map = AppMapUtils(self.url, self.project).get_app_map(from_time, to_time, access_token)
            for key in sorted(app_map.keys()):
                print(key)
        except Exception as e:
            raise e

    def get_logs(self, app_name, limit, from_time, to_time, since, regex_query, project, invert_match, context, older_context, newer_context):
        try:
            self._check_project(project)
            self.login(project)
            access_token = self.auth.get_saved_access_token(self.project)

            logReader = LogReader(self.project, self.url)
            context, older_context, newer_context = ContextualLogs().get_context_params(context, older_context, newer_context)

            start_time, end_time, limit, query = logReader.get_processed_params(app_name, limit, from_time, to_time, since, regex_query, invert_match, access_token, context)
            current_end_time = end_time

            while limit > 0 and int(current_end_time) > int(start_time):
                params = logReader.build_params(start_time, current_end_time, limit, query)
                logs = logReader.fetch_logs(params, access_token)

                if not logs:
                    break

                limit = limit - len(logs)
                current_end_time = str(int(logs[-1]["timestamp"]))

                if context:
                    ContextualLogs().print_contextual_logs(logs, logReader, app_name, older_context, newer_context, from_time, to_time, since, access_token, regex_query, [])
                else:
                    ContextualLogs().pretty_print(logs, regex_query)
        except Exception as e:
            raise e

    def list_projects(self):
        try:
            for project in self.valid_projects:
                if project == self.project:
                    print(project + " (currently set)")
                else:
                    print(project)    
        except Exception as e:
            logging.error(f"Error listing Loki projects: {e}")
            raise e

    def login(self, project):
        try:
            self._check_project(project)
            access_token = self.auth.get_saved_access_token(self.project)
            
            if not access_token:
                access_token = self.auth.get_new_access_token()
            
            auth_status = self.auth.get_auth_status(self.project, access_token)
            if auth_status:
                print("Login successful.")
            else:
                print("Login failed. Please login again. Loading login URL...")
                self.login(project)
        except Exception as e:
            logging.error(f"Error logging into Loki: {e}")
            raise e

    def get_version(self):
        print("Loki CLI v" + self.version)

def main():
    try:
        logfile_path = LokiConfig.get_file_path('lokicli.log')
        logging.basicConfig(filename=logfile_path, filemode='a', format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO)
        loki = LokiCLI()

        parser = argparse.ArgumentParser(description="Loki CLI")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        Subparsers(subparsers).create_parsers()
        args = parser.parse_args()

        if args.command == "login":
            loki.login(args.project)
        elif args.command == "set":
            loki.set_project(args.project)
        elif args.command == "projects":
            loki.list_projects()
        elif args.command == "apps":
            loki.list_apps(args.from_time, args.to_time, args.since, args.project)
        elif args.command == "logs":
            loki.get_logs(args.app, args.limit, args.from_time, args.to_time, args.since, args.query, args.project, args.invert_match, args.context, args.older_context, args.newer_context)
        elif args.command == "version":
            loki.get_version()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
