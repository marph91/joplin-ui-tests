"""Tests for the notelist in the center."""

import itertools

from parameterized import parameterized
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains

import base
import menu


class Notelist(base.Test):
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
        ActionChains(self.driver).send_keys(content)
        title_input = self.editor.find_element_by_xpath("//input[@class='title-input']")
        title_input.send_keys(title)

    @parameterized.expand(
        itertools.product(("note", "todo"), ("button", "hotkey", "top_menu"))
    )
    def test_create(self, type_, way):

        _, notebook_id = self.select_random_notebook()

        note_count = len(self.api.get_notes(notebook_id))
        self.add_note(way=way, todo=type_ == "todo")
        self.wait_for(
            lambda: len(self.api.get_notes(notebook_id)) == note_count + 1,
            message=f"Adding note by {way} failed.",
        )
