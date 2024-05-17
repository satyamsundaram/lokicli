import logging
from .config import LokiConfig

class Subparsers:
    def __init__(self, subparsers):
        self.subparsers = subparsers

        try:
            properties = LokiConfig().get_properties()
            self.defaultLimit = int(properties['logReader']['defaultLimit'])
        except Exception as e:
            logging.error(f"Error getting default limit: {e}")
            raise e

    def _create_set_project_parser(self):
        try:
            set_project_parser = self.subparsers.add_parser("set", help="Set the project in which your app is present (Use -h for help)")
            set_project_parser.add_argument("--project", "-p", required=True, help="[REQUIRED] Project in which your app belongs (s2s/ao3)")
            set_project_parser.usage = """
            lokicli set --project s2s                           # Set the project to s2s
            lokicli set -p ao3                                  # Set the project to ao3
            lokicli set --project=s2s                           # Set the project to s2s
            """
        except Exception as e:
            raise e

    def _create_list_apps_parser(self):
        try:
            list_apps_parser = self.subparsers.add_parser("apps", help="List all apps that have logged in a certain time period [default = last 1 hour] (Use -h for help)")
            list_apps_parser.add_argument("--from_time", "-f", help="From date and time (format, eg: 2024-01-22T10:30:00Z)")
            list_apps_parser.add_argument("--to_time", "-t", help="To date and time (format, eg: 2024-01-22T12:30:00Z)")
            list_apps_parser.add_argument("--since", "-s", default="1h", help="Since (format, eg: 30m, 1h, 24h) [default=1h]")
            list_apps_parser.add_argument("--project", "-p", help="[OPTIONAL] Project in which your app belongs (s2s/ao3)")

            list_apps_parser.usage = """
            (Either specify from_time and to_time or specify since, default = last 1 hour)
            
            lokicli apps                        # List apps that have logged in the last hour (default)
            lokicli apps --from_time 2024-01-22T10:00:00Z --to_time 2024-01-22T12:00:00Z  # List apps in a specific time range
            lokicli apps --since 2h             # List apps that have logged in the last 2 hours
            lokicli apps --project s2s          # List apps in the s2s project
            """
        except Exception as e:
            raise e
        
    def _create_list_projects_parser(self):
        try:
            list_projects_parser = self.subparsers.add_parser("projects", help="List all projects supported. (Use -h for help)")
            list_projects_parser.usage = """
            lokicli projects                                    # List all projects supported (shows project currently set)
            """
        except Exception as e:
            raise 

    def _version_parser(self):
        try:
            version_parser = self.subparsers.add_parser("version", help="Get current Loki CLI version. (Use -h for help)")
            version_parser.usage = """
            lokicli version                                    # Shows current Loki CLI version
            """
        except Exception as e:
            raise e
        
    def _login_parser(self):
        try:
            login_parser = self.subparsers.add_parser("login", help="Login to Lokicli. (Use -h for help)")
            login_parser.add_argument("--project", "-p", help="[OPTIONAL] Project in which your app belongs (s2s/ao3)")
            
            login_parser.usage = """
            lokicli login                                    # Login to currently set project (need to login for each project separately)
            lokicli login --project s2s                      # Login to s2s
            lokicli login -p ao3                             # Login to ao3
            """
        except Exception as e:
            raise e

    def _create_get_logs_parser(self):
        try:
            get_logs_parser = self.subparsers.add_parser("logs", help="Get logs for an app in a certain time period [default = last 1 hour]  (Use -h for help)")
            get_logs_parser.add_argument("--app", "-a", required=True, help="[REQUIRED] App name to retrieve logs for, eg: metro-default-prod")
            get_logs_parser.add_argument("--limit", "-l", type=int, default=self.defaultLimit, help="[OPTIONAL] Limit the number of logs to fetch (default=1000, max=500000)")
            get_logs_parser.add_argument("--from_time", "-f", help="From date and time (format, eg: 2024-01-22T10:30:00Z)")
            get_logs_parser.add_argument("--to_time", "-t", help="To date and time (format, eg: 2024-01-22T12:30:00Z)")
            get_logs_parser.add_argument("--since", "-s", default="1h", help="Since (format, eg: 30m, 1h, 24h) [default=1h]")
            get_logs_parser.add_argument("--query", "-q", help="[OPTIONAL] Query string to filter logs (can be regex as well).")
            get_logs_parser.add_argument("--project", "-p", help="[OPTIONAL] Project in which your app belongs (s2s/ao3)")
            get_logs_parser.add_argument("--invert-match", "-i", help="[OPTIONAL] Show non-matching log lines for a particular query. Use with --query", action="store_true")
            get_logs_parser.add_argument("--context", "-c", help="[OPTIONAL] Show context for a particular query. Use with --query. (eg: --context 5) this prints 5 lines before and after the matched line", type=int)
            get_logs_parser.add_argument("--older-context", "-o", help="[OPTIONAL] Show older context for a particular query. Use with --query. (eg: --older-context 5) this prints 5 lines before the matched line", type=int)
            get_logs_parser.add_argument("--newer-context", "-n", help="[OPTIONAL] Show newer context for a particular query. Use with --query. (eg: --newer-context 5) this prints 5 lines after the matched line", type=int)

            get_logs_parser.usage = """
            (Either specify from_time and to_time or specify since, default = last 1 hour)

            lokicli logs -a metro-default-prod                   # Get logs for the specified app (default: last 1 hour and 1000 logs)
            lokicli logs --app metro-default-prod
            lokicli logs -a metro-default-prod --from_time 2024-01-22T10:00:00Z --to_time 2024-01-22T12:00:00Z   # Get logs for the specified app in a specific time range
            lokicli logs -a metro-default-prod --since 2h        # Get logs for the specified app for the last 2 hours
            lokicli logs -a metro-default-prod --since 30m --limit 5000  # Get 5000 logs for the last 30 minutes
            lokicli logs -a metro-default-prod --query '\\d{4}-\\d{2}-\\d{2}'      # Get logs for the specified app with a specific query (it follows Google RE2 syntax)
            lokicli logs -a sms-ring-prod --project s2s          # Get logs for the specified app in the specified project
            lokicli logs -a sms-ring-prod --invert-match -q '\\d{4}-\\d{2}-\\d{2}'      # Get logs for the specified app that do not match the query
            lokicli logs -a sms-ring-prod -i -q '\\d{4}-\\d{2}-\\d{2}'      # Get logs for the specified app that do not match the query
            lokicli logs -a sms-ring-prod -c 5 -q '\\d{4}-\\d{2}-\\d{2}'      # Get context on the logs for the specified app that match the query
            lokicli logs -a sms-ring-prod -o 5 -q '\\d{4}-\\d{2}-\\d{2}'      # Get older context on the logs for the specified app that match the query
            lokicli logs -a sms-ring-prod -n 5 -q '\\d{4}-\\d{2}-\\d{2}'      # Get newer context on the logs for the specified app that match the query
            """
        except Exception as e:
            raise e

    def create_parsers(self):
        try:
            self._create_set_project_parser()
            self._create_list_apps_parser()
            self._create_list_projects_parser()
            self._create_get_logs_parser()
            self._login_parser()
            self._version_parser()
        except Exception as e:
            logging.error(f"Error creating parsers: {e}")
            raise e
