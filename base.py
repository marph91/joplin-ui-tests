"""Module for providing a test base."""

from datetime import datetime
import functools
import logging
import os
import random
import time
from typing import List, Optional
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
from selenium.webdriver.common.keys import Keys
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
        except:  # pylint: disable=bare-except
            message = f"{func.__name__}: first run failed! Repeat once..."
            logging.warning(message)
            print(message)
            pyautogui.click()  # focus the window
            func(self, *args, **kwargs)

    return wrapper


class IdGenerator:  # pylint: disable=too-few-public-methods
    """Generates contiguous integer IDs when called."""

    def __init__(self):
        self.id_int = 0

    def __call__(self) -> str:
        return_id = str(self.id_int).zfill(32)  # has to be 32 characters
        self.id_int += 1
        logging.debug(f"ID requested. Returned {return_id=}")
        return return_id


class Test(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName=methodName)

        self.new_id = IdGenerator()
        self.debug_dir = os.getenv("TEST_DEBUG_DIR")

    @classmethod
    def setUpClass(cls):
        cls.api = api
        cls.driver = driver

        # Each test class should have at least one notebook and one note.
        cls.api.add_notebook(title=cls.__name__)
        cls.api.add_note(title=cls.__name__)

        # cache common elements that shouldn't change
        cls.sidebar = cls.find_element_present(
            cls, By.CLASS_NAME, "rli-sideBar", timeout=10
        )
        cls.notebooks_title = cls.sidebar.find_element(
            By.XPATH, "//div[@data-folder-id]"
        )

        cls.notelist = cls.driver.find_element(By.CLASS_NAME, "rli-noteList")
        cls.editor = cls.driver.find_element(By.CLASS_NAME, "rli-editor")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Clear all notes at the end of the test class.
        cls.api.delete_all_notebooks()

    def setUp(self):
        super().setUp()
        logging.debug(f"Starting test {self.id()}")
        self.start_time = time.time()

    def tearDown(self):
        super().tearDown()

        # add the duration to each test
        print(f"{time.time() - self.start_time:.3f} s, ", end="", flush=True)

        if any(error for _, error in self._outcome.errors if error is not None):
            datestr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            base_name = f"{self.debug_dir}/{datestr}_{self.id()}"

            # save screenshots of electron app and xvfb
            self.driver.get_screenshot_as_file(f"{base_name}_webdriver.png")
            ImageGrab.grab().save(f"{base_name}_xvfb.png", "PNG")
            # save the browser log
            with open(f"{base_name}_browser_log.txt", "w") as outfile:
                log = self.driver.get_log("browser")
                outfile.write("\n".join([str(line) for line in log]))

        pyautogui.press("esc")  # close open dialog, if any

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

    def find_element_present(self, by_, locator, timeout: int = 1):
        """Find an element and wait until it's present."""
        # https://stackoverflow.com/a/59130336/7410886
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by_, locator))
        )

    def find_element_visible(self, by_, locator, timeout: int = 1):
        """Find an element and wait until it's visible."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by_, locator))
        )

    def find_element_clickable(self, by_, locator, timeout: int = 1):
        """Find an element and wait until it's visible."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by_, locator))
        )

    def assert_contains(self, container, element):
        """Assert that one element contains another."""
        # TODO: Is there a better way?
        self.assertNotEqual(element.get_attribute("outerHTML").strip(), "")
        self.assertIn(
            element.get_attribute("outerHTML"), container.get_attribute("outerHTML")
        )

    def is_focussed(self, element) -> bool:
        """Check if an element is in focus."""
        # https://stackoverflow.com/a/11998624/7410886
        return element == self.driver.switch_to.active_element

    def get_notebooks(self):
        logging.debug("UI: get notebooks")
        # First match is the "All notes" button.
        return self.sidebar.find_elements(By.CLASS_NAME, "list-item-container")[1:]

    def get_notes(self):
        logging.debug("UI: get notes")
        # Finds notes and todos.
        return self.notelist.find_elements(
            By.XPATH, "//div[contains(@class, '-list-item')]"
        )

    def scroll_vertical(self, element, height: int):
        self.driver.execute_script(
            "arguments[0].scrollBy(0, arguments[1])", element, height
        )

    def delete_note(self, element, way: str = "hotkey"):
        logging.debug(f"UI: delete note {way=}")

        if way == "hotkey":
            element.click()
            pyautogui.press("delete")
        elif way == "right_click":
            ActionChains(self.driver).context_click(element).perform()
            menu.choose_entry(8)
        else:
            ValueError("Not supported")

        # left button to confirm
        menu.choose_entry(1, key="left")

    def select_random_notebook(self, exclude: Optional[List[str]] = None):
        notebooks = self.api.get_all_notebooks()
        if exclude is not None:
            # TODO: Could be problematic for multiple time nested notebook.
            notebooks = [
                notebook
                for notebook in notebooks
                if notebook["id"] not in exclude
                and notebook["parent_id"] not in exclude
            ]
        notebook_id = random.choice(notebooks)["id"]
        notebook_element = self.sidebar.find_element(
            By.XPATH, f"//div[@data-folder-id='{notebook_id}']"
        )
        notebook_element.click()
        return notebook_element, notebook_id

    def select_random_note(self, exclude: Optional[List[str]] = None):
        notes = self.api.get_all_notes()
        if exclude is not None:
            notes = [note for note in notes if note["id"] not in exclude]
        note = random.choice(notes)

        # click containing folder to show note
        notebook_element = self.find_element_present(
            By.XPATH, f"//div[@data-folder-id='{note['parent_id']}']"
        )
        notebook_element.click()

        note_element = self.find_element_present(
            By.XPATH, f"//a[@data-id='{note['id']}']"
        )
        note_element.click()
        return note_element, note["id"], notebook_element, note["parent_id"]

    def get_random_tag(self):
        # Don't click the tag, since loading the note takes time.
        tags = self.api.get_all_tags()
        tag_id = random.choice(tags)["id"]
        tag_element = self.driver.find_element(
            By.XPATH, f"//div[@data-tag-id='{tag_id}']"
        )
        return tag_element, tag_id

    def fill_modal_dialog(
        self,
        input_: str,
        confirm_by_button: bool = False,
        notebook: bool = False,
        tag: bool = False,
        wait_before_confirm: Optional[float] = None,
    ):
        """Fill out and confirm a modal dialog with one input."""
        # There are two modal dialogs. Chose the one that is displayed.
        dialog = self.find_element_visible(
            By.XPATH,
            "//div[@class='dialog-root']"
            if notebook
            else "//div[@class='modal-layer'][contains(@style, 'display: flex')]",
        )
        input_element = dialog.find_element(By.TAG_NAME, "input")
        # Sometimes clear() and other workarounds don't work.
        # Use backspace instead. It takes longer, but works reliably.
        # See: https://stackoverflow.com/a/50682169/7410886
        while input_element.get_attribute("value") != "":
            input_element.send_keys(Keys.BACKSPACE)
        input_element.send_keys(input_)
        if wait_before_confirm is not None:
            time.sleep(wait_before_confirm)
        if tag:
            input_element.send_keys(Keys.ENTER)
        if confirm_by_button:
            # Assume the first button is to confirm.
            confirm_button = dialog.find_element(By.TAG_NAME, "button")
            confirm_button.click()
        else:
            input_element.send_keys(Keys.ENTER)

    def get_notebook_count_api(self):
        return len(self.api.get_all_notebooks())

    def get_note_count_api(self):
        return len(self.api.get_all_notes())

    def get_tag_count_api(self):
        return len(self.api.get_all_tags())
