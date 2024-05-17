## Guide to using Loki CLI for querying logs stored in Loki
### 1. Install lokicli:
```bash
# if you had previously installed lokicli via the setup script, remove it

# for Unix
sudo rm /usr/local/bin/lokicli
# remove this line: "export PATH=/usr/local/bin:$PATH" from ~/.bashrc or ~/.zshrc

# for Windows (in administrator mode)
del "C:\\bin\lokicli.exe"
echo %PATH% # check if this PATH exists: PATH "C:\\bin;%PATH%"
setx PATH "%PATH:;C:\bin=%" # if yes, remove it
echo %PATH% # verify the PATH
```

```bash
# for fresh installation or upgrade
pip install --trusted-host --index-url # nexus repository package url
```

### 2. Set project
When you set a project, lokicli runs your commands against that project unless you specify the project name using --project/-p flag to list or get, in which case the project gets overwritten for the subsequent commands.
```bash
lokicli set -h

lokicli set --project=ao3
# or
lokicli set --project s2s
# or
lokicli set -p ao3
```

### 3. Login to project
To login, you'll need to open the link in your browser, authenticate using your account and then copy the URL on the page that shows 403 Forbidden and paste it back to the CLI.
```bash
lokicli login -h

lokicli login
# or
lokicli login --project s2s
# or
lokicli login -p ao3
```

### 4. List projects
```bash
lokicli projects -h

lokicli projects # list projects currently supported (shows currently set project)
```

### 5. List apps
```bash
lokicli apps -h

# List apps that have logged in the last hour (default)
lokicli apps   

# you can change the lookback period if your app is not present in the list
lokicli apps -s 24h
lokicli apps -s 72h
lokicli apps -s 30m
lokicli apps --since 2h
lokicli apps --since=6h

# List apps in a specific time range
lokicli apps --from_time 2024-01-22T10:00:00Z --to_time 2024-01-22T12:00:00Z     

# List apps in the s2s project               
lokicli apps --project s2s 
```

**An example list of what the above command returns:**
(similar naming convention to how it is on argo)
```
event-exporter-default-monitoring
intentmatch-default-prod
intentmatch-restart-cron-cron-prod
nero-v2-man.m-stage
nn-splitter-wrapper-prod
sonarqube-default-sonarqube
topix-data-pipeline-aggregator-default-prod
```

### 6. Get logs for an application
Copy its app name from the above list and paste it as shown:
- By default it'll always return 1000 log lines but you can configure it using the -l/--limit flag
- By default it'll always return logs for the last 1 hour but you can cofigure it using -s/--since flag or --from_time/-f and --to_time/-t flags to return logs from some other time range
```bash
lokicli logs -h

# Get logs for the specified app (default: last 1 hour and 1000 logs)
lokicli logs -a nitro-default-prod
lokicli logs --app nitro-default-prod

# Get 5000 logs from the last 2 hrs
lokicli logs -a nitro-default-prod --since 2h --limit 5000

# loki returns logs  backwards in time, aka from the latest timestamp to the oldest timestamp
lokicli logs -a topix-nero-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 50000
lokicli logs -a spacy-en-default-prod --from_time 2024-01-22T00:30:00Z --to_time 2024-01-22T06:00:00Z -l 400000

# invert-match a query
lokicli logs -a intentmatch-default-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 --query "Error" --invert-match
# or using short hand flag
lokicli logs -a intentmatch-default-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 -q "Error" -i

# regex pattern matching
lokicli logs -a intentmatch-default-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 --query "Error"
lokicli logs -a intentmatch-default-prod --from_time=2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 -q "\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
lokicli logs -a intentmatch-default-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 --query=".*/autoopt/.*"

# some more preprocessing
lokicli logs -a spacy-en-default-prod -f 2024-01-22T06:30:00Z -t 2024-01-22T10:00:00Z -l 4000 > logs
lokicli logs -a spacy-en-default-prod -f 2024-01-22T06:30:00Z -t 2024-01-22T10:00:00Z -l 4000 | less
lokicli logs -a intentmatch-default-prod -f 2024-01-22T00:00:00Z -t 2024-01-22T05:00:00Z -l 5000 -q ".*/autoopt/.*" | grep "autoopt"
```

### Help
```
# use either of the commands below to learn more
lokicli -h
lokicli --help
```

## Lokicli stats:
On an average, it takes 4-6 seconds to fetch 1000 logs for an app from Loki.
If your app's logs are fairly large, it may take longer.

### FAQ
**Q.** I can’t find my app name when I use lokicli to list apps.
**Sol:** The default lookback period for lokicli is 1 hour, that is, if your app emitted logs in the past 1hr, it’ll be visible in the list when you run lokicli to list apps. If you don’t see your app name, then you can try increasing the lookback period say to 24h like this: `lokicli list apps -s 24h`

**Q.** I can’t find my app name in the Loki dashboard dropdown list.
**Sol:** The default lookback period is 1 hour. If your app didn’t emit any logs in the past 1hr, it won’t be present in the dropdown list. Try increasing the lookback period using the option present in the top bar (right side).

**Q.** Can we tail the logs?
**Sol:** As of now, lokicli does not provide any option to tail the logs.

**Q.** Why am I getting the error: `Error getting app map: 400`?
**Sol:** Please ensure that the time range is within the last 30 days and not beyond that.


**Q.** What is the format for the datetime and what is the default timezone while using lokicli?
**Sol:** The default timezone is UTC and the datetime format is Unix timestamp both of which are fixed and not configurable.

**Q.** Is regex supported?
**Sol:** Yes, regex is supported. You can refer to examples above.

**Q.** How are the logs being aggregated if my app has multiple pods?
**Sol:** Loki aggregates the logs from all the pods of an app, sorts them by time and then returns them.

**Q.** The query did not return anything. What's wrong?
**Sol:** If the query returned without any results, it means that for that app and in that time period there were no logs. Also, note that loki only stores logs for the last 30 days, so you'll get no logs if you query for logs beyond the last 30 days. If the query returned with a error, run `lokicli help` to debug.

**Q.** Why do I see this error when querying something in the logs? `Error: Error fetching logs: 400.`.
**Sol:** Please check you regex query and ensure the regex query is according to the [Google RE2 syntax](https://github.com/google/re2/wiki/Syntax).
