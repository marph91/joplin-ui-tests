"""Utilities to interact with the API."""

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

    def create_url(self, path: str, query: Optional[dict]) -> str:
        if query is None:
            query = {}
        query["token"] = self.token  # TODO: extending the dict may have side effects
        query_str = "&".join([f"{key}={val}" for key, val in query.items()])
        return f"{self.url}{path}?{query_str}"

    def get(self, path: str, query: Optional[dict] = None):
        response = requests.get(self.create_url(path, query))
        if response.status_code != 200:
            print(response.json)
        response.raise_for_status()
        return response

    def post(
        self, path: str, query: Optional[dict] = None, data: Optional[dict] = None
    ):
        response = requests.post(self.create_url(path, query), json=data)
        if response.status_code != 200:
            print(response.json)
        response.raise_for_status()
        return response

    def ping(self):
        return self.get("/ping")

    def get_notebooks(self, parent_id=None):
        # TODO: Parent doesn't seem to be supported.
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        return self.get(f"{parent}/folders").json()["items"]

    def get_notes(self, parent_id=None):
        parent = "" if parent_id is None else f"/folders/{parent_id}"
        return self.get(f"{parent}/notes").json()["items"]

    def add_notebook(self, name: str = "test", parent_id=None):
        data = {"title": name}
        if parent_id:
            data["parent_id"] = parent_id
        self.post("/folders", data=data)

    def add_note(
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


# Wait until a note has loaded, since notes load slowest.
# TODO: This only works when a notebook with notes is selected.
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "note-list-item"))
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
try:
    api.get_notes()
except requests.exceptions.ConnectionError:
    # try a second time
    api.get_notes()
buttons[-1].click()  # back button
