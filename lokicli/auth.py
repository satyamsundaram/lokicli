#!usr/bin/env python3

import requests
import logging
import os

from .config import LokiConfig

class Auth:
    def __init__(self, url):
        self.url = url
        self.AUTH_FILE = LokiConfig().get_file_path('lokicli.auth')

    def save_access_token(self, project, cookie):
        flag=0
        
        try:
            with open(self.AUTH_FILE, "a") as file:
                pass

            with open(self.AUTH_FILE, "r") as file:
                file_content = file.read().strip()
                for line in file_content.splitlines():
                    if line.startswith(project):
                        file_content = file_content.replace(line, project + ":" + cookie)
                        flag=1
                        break
            
            if flag==1:
                with open(self.AUTH_FILE, "w") as file:
                    file.write(file_content)
            else:
                with open(self.AUTH_FILE, "a") as file:
                    file.write("\n" + project + ":" + cookie)
        except Exception as e:
            logging.error(f"Error saving cookie for project {project}: {e}")
            raise e

    def get_saved_access_token(self, project):
        try:
            if os.path.exists(self.AUTH_FILE):
                with open(self.AUTH_FILE, "r") as file:
                    file_content = file.read().strip()
                    for line in file_content.splitlines():
                        if line.startswith(project):
                            return line.split(":")[1]
            else:
                return ""
        except Exception as e:
            logging.error(f"Error loading cookie for project {project}: {e}")
            raise e

    @staticmethod
    def get_response_header(response, prefix):
        for header in response.headers:
            if response.headers[header].lower().startswith(prefix):
                return response.headers[header]
        return ""

    def get_csrf_token(self, response):
        response_header = self.get_response_header(response, "_oauth2_proxy_csrf")
        return response_header.split(";")[0][19:] if response_header else ""

    def get_access_token(self, response):
        response_header = self.get_response_header(response, "_oauth2_proxy_csrf")
        return response_header.split(",")[2].split(";")[0][15:] if response_header else ""

    def exchange_tokens(self, csrf_token, callback_url):
        try:
            cookies = {"_oauth2_proxy_csrf": csrf_token}
            response = requests.get(callback_url, cookies=cookies, allow_redirects=False)

            if response.status_code == 302:
                access_token = self.get_access_token(response)
                if access_token:
                    return access_token
                else:
                    raise Exception("Failed to retrieve access token cookie.")
            else:
                raise Exception(f"Error exchanging for access token: {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"Error getting access token: {e}")
            raise e

    def get_new_access_token(self):
        try:
            response = requests.get(self.url, allow_redirects=False)

            if response.status_code == 302:
                auth_start_url = self.get_response_header(response, "https")
                response = requests.get(auth_start_url, allow_redirects=False)

                if response.status_code == 302:
                    csrf_token = self.get_csrf_token(response)
                    redirect_url = self.get_response_header(response, "https")

                    if csrf_token and redirect_url:
                        print(f"Please login and authorize access at: {redirect_url}")
                        print("Once authorized, copy and paste the callback URL here: ")

                        callback_url = input("Callback URL: ")

                        access_token = self.exchange_tokens(csrf_token, callback_url)
                        return access_token
                    else:
                        raise Exception("Failed to retrieve CSRF token and redirect URL.")
                else:
                    raise Exception(f"Failed to authenticate to oauth2-proxy: ({response.status_code}) {response.text}")
            else:
                raise Exception(f"Failed to start auth flow: ({response.status_code}) {response.text}")
        except Exception as e:
            logging.error(f"Error getting login access token: {e}")
            raise e

    def delete_access_token(self, project):
        try:
            with open(self.AUTH_FILE, "r") as file:
                file_content = file.read().strip()
                for line in file_content.splitlines():
                    if line.startswith(project):
                        file_content = file_content.replace(line, "".strip())
                        break

            with open(self.AUTH_FILE, "w") as file:
                file.write(file_content)
        except Exception as e:
            logging.error(f"Error deleting cookie for project {project}: {e}")
            raise e

    def get_auth_status(self, project, access_token):
        try:
            cookies = {"_oauth2_proxy": access_token}
            loki_response = requests.get(self.url, cookies=cookies, allow_redirects=False)
            
            if loki_response.status_code == 200:
                self.save_access_token(project, access_token)
                return 1
            else:
                self.delete_access_token(project)
                return 0
        except Exception as e:
            logging.error(f"Error checking auth status: {e}")
            raise e
