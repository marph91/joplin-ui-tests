"""Module for providing a test base."""

from datetime import datetime
import functools
import os
import random
import time
import unittest

from PIL import ImageGrab

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


def run_again_at_failure(func):
    """
    Simply run the test again in case of a failure.
    Useful to check if the failure is persistent.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except:
            print(f"{func.__name__}: first run failed!")
            func(self, *args, **kwargs)

    return wrapper


class IdGenerator:
    """Generates contiguous integer IDs when called."""

    def __init__(self):
        self.id_int = 0

    def __call__(self) -> str:
        return_id = str(self.id_int).zfill(32)  # has to be 32 characters
        self.id_int += 1
        return return_id


class Test(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName=methodName)

        self.new_id = IdGenerator()

    @classmethod
    def setUpClass(cls):
        os.makedirs("debug", exist_ok=True)

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
        cls.editor_toolbar = cls.editor.find_element_by_class_name("editor-toolbar")

    def tearDown(self):
        super().tearDown()

        for _, error in self._outcome.errors:
            if error:
                datestr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                self.driver.get_screenshot_as_file(
                    f"debug/{datestr}_{self.id()}_webdriver.png"
                )
                screenshot = ImageGrab.grab()
                screenshot.save(f"debug/{datestr}_{self.id()}_xvfb.png", "PNG")

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
        # Finds notes and todos.
        return self.notelist.find_elements_by_xpath(
            "//div[contains(@class, '-list-item')]/a"
        )

    def scroll_vertical(self, element, height: int):
        self.driver.execute_script(
            "arguments[0].scrollBy(0, arguments[1])", element, height
        )

    def delete_note(self, element, way: str = "hotkey"):

        if way == "hotkey":
            element.click()
            pyautogui.press("delete")
        elif way == "right_click":
            ActionChains(self.driver).context_click(element).perform()
            menu.choose_entry(8)
        else:
            ValueError("Not supported")

        # left button to confirm
        # TODO: Selectable via webdriver?
        # TODO: Why are two clicks necessary?
        menu.choose_entry(2, key="left")

    def select_random_notebook(self):
        notebooks = self.api.get_notebooks()
        notebook_id = random.choice(notebooks)["id"]
        notebook_element = self.driver.find_element_by_xpath(
            f"//div[@data-folder-id='{notebook_id}']"
        )
        notebook_element.click()
        return notebook_element, notebook_id

    def select_random_note(self):
        notes = self.api.get_notes()
        note = random.choice(notes)

        # click containing folder to show note
        notebook_element = self.driver.find_element_by_xpath(
            f"//div[@data-folder-id='{note['parent_id']}']"
        )
        notebook_element.click()

        note_element = self.driver.find_element_by_xpath(
            f"//a[@data-id='{note['id']}']"
        )
        note_element.click()
        return note_element, note["id"]
