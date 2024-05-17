#!/usr/bin/env python3

from datetime import datetime, timezone, timedelta
import re
import logging

class LokiTimeUtils:
    @staticmethod
    def utc_to_unix_nanosecond_epoch(utc_timestamp):
        utc_datetime = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        timestamp_seconds = utc_datetime.timestamp()
        timestamp_nanoseconds = str(timestamp_seconds).split('.')[0] + "0"*9
        return int(timestamp_nanoseconds)

    @staticmethod
    def unix_nanosecond_epoch_to_utc(timestamp_nanoseconds):
        timestamp_seconds = timestamp_nanoseconds / 1e9
        utc_datetime = datetime.utcfromtimestamp(timestamp_seconds)
        utc_timestamp = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return utc_timestamp

    @staticmethod
    def _parse_since(since):
        if len(since) < 2 or since[-1] not in ["m", "h"]:
            raise ValueError("Invalid format for since. Specify value in minutes or hours eg: 30m or 1h.")
       
        unit = since[-1]
        value = int(since[:-1])

        if unit == "h":
            return timedelta(hours=value)
        elif unit == "m":
            return timedelta(minutes=value)
        else:
            raise ValueError("Invalid unit in since. Use 'h' for hours or 'm' for minutes.")

    @staticmethod
    def _check_from_and_to_times(from_time, to_time):
        if (from_time and not to_time) or (to_time and not from_time):
            raise ValueError("Both 'from_time' and 'to_time' times must be specified.")

        time_format = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
        if not re.match(time_format, from_time):
            raise ValueError("Invalid 'from_time'. Correct format is: YYYY-MM-DDTHH:MM:SSZ.")
        
        if not re.match(time_format, to_time):
            raise ValueError("Invalid 'to_time'. Correct format is: YYYY-MM-DDTHH:MM:SSZ.")
        
        if from_time >= to_time:
            raise ValueError("'from_time' cannot be after 'to_time'.")

    def get_from_and_to_times(self, from_time, to_time, since): 
        try:     
            if from_time or to_time:
                self._check_from_and_to_times(from_time, to_time)
                return from_time, to_time

            to_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            time_delta = self._parse_since(since)
            from_time = (datetime.now(timezone.utc) - time_delta).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            logging.error(f"Error getting from and to times: {e}")
            raise e
        return from_time, to_time
