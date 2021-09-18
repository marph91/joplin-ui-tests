"""Utilities to interact with the API."""

from driver import driver
import menu

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Api:
    def __init__(self, token):
        self.url = "http://localhost:41184"
        self.token = token

    def ping(self):
        response = requests.get(f"{self.url}/ping")
        response.raise_for_status()
        return response

    def get_notebooks(self, parent_id=None):
        # TODO: Parent doesn't seem to be supported.
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        response = requests.get(f"{self.url}{parent}/folders?token={self.token}")
        response.raise_for_status()
        return response.json()["items"]

    def get_notes(self, parent_id=None):
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        response = requests.get(f"{self.url}{parent}/notes?token={self.token}")
        response.raise_for_status()
        return response.json()["items"]


# wait until the driver has loaded
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "rli-sideBar"))
)

# activate the api if not already done
menu.top(["Tools", "Options"])
web_clipper_tab = driver.find_element_by_xpath("//a/span[text()='Web Clipper']")
web_clipper_tab.click()
token = driver.find_element_by_xpath("//span[string-length(text())=128]")
api = Api(token.text)

# avoid any language specific locators
buttons = driver.find_elements_by_tag_name("button")
try:
    api.ping()
except requests.exceptions.ConnectionError:
    buttons[0].click()  # activate button
api.ping()
buttons[-1].click()  # back button
