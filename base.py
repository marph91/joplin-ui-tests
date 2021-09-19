"""Module for providing a test base."""

import time
import unittest

# Only import pyautogui now, because it uses the DISPLAY variable.
# It is set when starting xvfb.
# https://pynput.readthedocs.io/en/latest/limitations.html?highlight=display#linux
# It is needed to navigate through the menus, since they seem to be system level,
# which can't be handled by selenium.
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from api import api
from driver import driver
import menu


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = api
        cls.driver = driver

        # cache common elements that shouldn't change
        cls.sidebar = WebDriverWait(cls.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rli-sideBar"))
        )
        cls.notebooks_title = cls.sidebar.find_element_by_xpath(
            "//div[@data-folder-id]"
        )
        cls.notebooks_div = cls.sidebar.find_element_by_xpath(
            "//div[starts-with(@class, 'folders')]"
        )

        cls.notelist = cls.driver.find_element_by_class_name("rli-noteList")
        cls.editor = cls.driver.find_element_by_class_name("rli-editor")

    @staticmethod
    def wait_for(
        func,
        *args,
        timeout: int = 1,
        interval: float = 0.1,
        initial_delay: bool = False,
        message: str = "",
        **kwargs,
    ):
        # https://stackoverflow.com/a/2785908/7410886
        mustend = time.time() + timeout
        if not initial_delay:
            if func(*args, **kwargs):
                return
        while time.time() < mustend:
            if func(*args, **kwargs):
                return
            time.sleep(interval)
        raise TimeoutError(message)

    def get_notebooks(self):
        # First match is the "All notes" button.
        return self.notebooks_div.find_elements_by_class_name("list-item-container")[1:]

    def get_notes(self):
        return self.notelist.find_elements_by_class_name("note-list-item")

    def add_notebook(self, name: str = "test", way: str = "button", parent=None):

        if way == "button":
            add_notebook_button = self.sidebar.find_element_by_xpath(
                "//div[@data-folder-id]/following-sibling::button"
            )
            add_notebook_button.click()
        elif way == "right_click":
            if parent is None:
                # right click on the notebooks title at top
                notebook_title = self.driver.find_element_by_xpath(
                    "//div[@data-folder-id]"
                )

                # first and only option of dropdown
                # TODO: Find a way to abstract all menus.
                ActionChains(self.driver).context_click(notebook_title).perform()
                menu.choose_entry(1)
            else:
                # right click on the specified parent notebook
                ActionChains(self.driver).context_click(parent).perform()
                menu.choose_entry(1)  # first option of dropdown
        elif way == "top_menu":
            if parent is None:
                menu.top(["File", "New notebook"])
            else:
                parent.click()
                menu.top(["File", "New sub-notebook"])
        else:
            ValueError("Not supported")

        add_notebook_dialog = self.driver.find_element_by_class_name("modal-dialog")
        notebook_title_input = add_notebook_dialog.find_element_by_tag_name("input")
        notebook_title_input.send_keys(name)
        add_notebook_buttons = add_notebook_dialog.find_elements_by_tag_name("button")

        [b for b in add_notebook_buttons if b.text == "OK"][0].click()

    def add_note(
        self,
        way: str = "button",
        title: str = "test_title",
        content: str = "test_content",
        todo: bool = False,
    ):

        if way == "button":
            add_note_button = self.notelist.find_element_by_class_name(
                "new-todo-button" if todo else "new-note-button"
            )
            add_note_button.click()
        elif way == "hotkey":
            # ActionChains doesn't work.
            pyautogui.keyDown("ctrl")
            pyautogui.press("t" if todo else "n")
            pyautogui.keyUp("ctrl")
        elif way == "top_menu":
            menu.top(["File", "New to-do" if todo else "New note"])
        else:
            ValueError("Not supported")

        # Editor should be focused automatically.
        ActionChains(driver).send_keys(content)
        title_input = self.editor.find_element_by_xpath("//input[@class='title-input']")
        title_input.send_keys(title)
