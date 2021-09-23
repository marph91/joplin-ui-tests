"""Utilities to interact with the API."""

import logging
import time
from typing import Optional

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver import driver
import menu


class Api:
    def __init__(self, token):
        self.url = "http://localhost:41184"
        self.token = token

    def create_url(self, path: str, query: Optional[dict] = None) -> str:
        if query is None:
            query = {}
        query["token"] = self.token  # TODO: extending the dict may have side effects
        query_str = "&".join([f"{key}={val}" for key, val in query.items()])
        return f"{self.url}{path}?{query_str}"

    def get(self, path: str, query: Optional[dict] = None):
        logging.debug(f"API: get request: {path=}, {query=}")
        response = requests.get(self.create_url(path, query))
        if response.status_code != 200:
            print(response.json())
        response.raise_for_status()
        return response

    def post(
        self, path: str, query: Optional[dict] = None, data: Optional[dict] = None
    ):
        logging.debug(f"API: post request: {path=}, {query=}, {data=}")
        response = requests.post(self.create_url(path, query), json=data)
        if response.status_code != 200:
            print(response.json())
        response.raise_for_status()
        return response

    def delete(self, path: str):
        logging.debug(f"API: delete request: {path=}")
        response = requests.delete(self.create_url(path))
        if response.status_code != 200:
            print(response.json())
        response.raise_for_status()
        return response

    def ping(self):
        return self.get("/ping")

    def get_notebooks(self, parent_id: str = None):
        # TODO: Parent doesn't seem to be supported.
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        return self.get(f"{parent}/folders").json()["items"]

    def get_notes(self, parent_id: str = None, query=None):
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        return self.get(f"{parent}/notes", query=query).json()["items"]

    def get_tags(self):
        return self.get("/tags").json()["items"]

    def get_note(self, id_: str = None, query=None):
        return self.get(f"/notes/{id_}", query=query).json()

    def add_notebook(self, name: str = "test", parent_id: str = None):
        data = {"title": name}
        if parent_id:
            data["parent_id"] = parent_id
        self.post("/folders", data=data)

    def add_note(  # pylint: disable=too-many-arguments
        self,
        name: str = "test",
        content: str = "test_content",
        id_: Optional[str] = None,
        parent_id: Optional[str] = None,
        todo: bool = False,
    ):
        data = {"title": name, "body": content, "is_todo": int(todo)}
        if parent_id is not None:
            data["parent_id"] = parent_id
        if id_ is not None:
            data["id"] = id_
        self.post("/notes", data=data)

    def delete_notebook(self, id_):
        self.delete(f"/folders/{id_}")

    def delete_all_notebooks(self):
        notebooks = self.get_notebooks()
        for notebook in notebooks:
            # Deleting the root notebooks is sufficient.
            if not notebook["parent_id"]:
                self.delete_notebook(notebook["id"])


# Wait until an element has loaded to continue.
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "rli-sideBar"))
)

# activate the api if not already done
menu.top(["Tools", "Options"])
web_clipper_tab = driver.find_element_by_xpath("//a/span[text()='Web Clipper']")
web_clipper_tab.click()
api = Api(driver.find_element_by_xpath("//span[string-length(text())=128]").text)

# avoid any language specific locators
buttons = driver.find_elements_by_tag_name("button")
try:
    api.ping()
except requests.exceptions.ConnectionError:
    buttons[0].click()  # activate button

# try three times until the API is available
for i in range(3):
    try:
        logging.debug(f"API: ping, try {i + 1}")
        api.ping()
        break
    except requests.exceptions.ConnectionError:
        # try another time
        time.sleep(0.1)
api.ping()
logging.debug("API: ping successful")

buttons[-1].click()  # back button
