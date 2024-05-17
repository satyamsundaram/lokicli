#!usr/bin/env python3

import re
import colorama
import logging

class ContextualLogs:
    def __init__(self):
        pass

    @staticmethod
    def get_contextual_logs(logReader, app_name, context, from_time, to_time, since, access_token, item, direction):
        try:
            start_time, end_time, limit, query = logReader.get_processed_params(app_name, context, from_time, to_time, since, "", False, access_token, 0)
            time_range = 100000000000000

            params = {
                    "direction": direction,
                    "end": str(int(item["timestamp"]) + time_range) if direction == "FORWARD" else item["timestamp"],
                    "limit": context+1 if direction == "FORWARD" else context,
                    "query": query,
                    "start": item["timestamp"] if direction == "FORWARD" else str(int(item["timestamp"]) - time_range),
                }

            return logReader.fetch_logs(params, access_token)
        except Exception as e:
            logging.error(f"Error getting forward contextual logs: {e}")
            raise e

    @staticmethod
    def merge_lists(list1, list2):
        try:
            merged_list = []
            seen_timestamps = set()

            for item in list1 + list2:
                if item["timestamp"] not in seen_timestamps:
                    merged_list.append(item)
                    seen_timestamps.add(item["timestamp"])

            return merged_list
        except Exception as e:
            logging.error(f"Error merging lists: {e}")
            raise e

    @staticmethod
    def get_context_params(context, older_context, newer_context):
        try:
            if context:
                older_context = context if not older_context else older_context
                newer_context = context if not newer_context else newer_context

            elif older_context and not newer_context:
                newer_context = 0

            elif newer_context and not older_context:
                older_context = 0

            context = max(older_context, newer_context) if older_context or newer_context else 0

            return context, older_context, newer_context
        except Exception as e:
            logging.error(f"Error getting context params: {e}")
            raise e

    @staticmethod
    def pretty_print(logs, regex_query):
        try:
            colorama.init()

            highlight_color = colorama.Fore.RED
            reset_color = colorama.Style.RESET_ALL
            style_color = colorama.Style.BRIGHT

            for item in logs:
                if regex_query:
                    matches = list(re.finditer(regex_query, item["log"]))
                    if matches:
                        highlighted_log = item["log"]
                        for match in reversed(matches):
                            start, end = match.span()
                            matched_text = item["log"][start:end]
                            highlighted_text = highlight_color + style_color + matched_text + reset_color
                            highlighted_log = highlighted_log[:start] + highlighted_text + highlighted_log[end:]

                        print(highlighted_log)
                    else:
                        print(item["log"])
                else:
                    print(item["log"])
        except Exception as e:
            logging.error(f"Error pretty printing logs: {e}")
            raise e

    def print_contextual_logs(self, logs, logReader, app_name, older_context, newer_context, from_time, to_time, since, access_token, regex_query, current_context):
        try:
            for item in logs:
                if newer_context:
                    forward_contextual_logs = self.get_contextual_logs(logReader, app_name, newer_context, from_time, to_time, since, access_token, item, "FORWARD")
                    if older_context:
                        backward_contextual_logs = self.get_contextual_logs(logReader, app_name, older_context, from_time, to_time, since, access_token, item, "BACKWARD")

                if older_context and not newer_context:
                    backward_contextual_logs = self.get_contextual_logs(logReader, app_name, older_context, from_time, to_time, since, access_token, item, "BACKWARD")
                    backward_contextual_logs.insert(0, item)

                if current_context:
                    if newer_context and forward_contextual_logs[-1]["timestamp"] >= current_context[-1]["timestamp"]:
                        full_context = list(reversed(forward_contextual_logs))
                        if older_context:
                            full_context.extend(backward_contextual_logs)
                        current_context = self.merge_lists(current_context, full_context)

                    elif older_context and backward_contextual_logs[0]["timestamp"] >= current_context[-1]["timestamp"]:
                        full_context = backward_contextual_logs
                        current_context = self.merge_lists(current_context, full_context)

                    else:
                        self.pretty_print(current_context, regex_query)
                        print("\n---\n")
                        current_context = []

                if not current_context:
                    if newer_context:
                        current_context.extend(list(reversed(forward_contextual_logs)))
                    if older_context:
                        current_context.extend(backward_contextual_logs)

            self.pretty_print(current_context, regex_query)
        except Exception as e:
            logging.error(f"Error printing contextual logs: {e}")
            raise e