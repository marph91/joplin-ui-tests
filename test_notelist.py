"""Tests for the notelist in the center."""

import itertools

from parameterized import parameterized
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains

import base
import menu


class Note(base.Test):
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
            pyautogui.hotkey("ctrl", "t" if todo else "n")
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
        self.add_note(title=self._testMethodName, way=way, todo=type_ == "todo")
        self.wait_for(
            lambda: len(self.api.get_notes(notebook_id)) == note_count + 1,
            message=f"Adding note by {way} failed.",
        )

    @parameterized.expand(("hotkey", "right_click"))
    def test_delete_note(self, way):
        self.skipTest("TODO: Running this test causes multiple tests to fail.")
        # TODO: check if correct note got deleted

        # Create a dummy note to keep the count constant.
        self.api.add_note()

        note_element, _ = self.select_random_note()
        note_count = len(self.api.get_notes())
        self.delete_note(note_element, way=way)
        self.wait_for(
            lambda: len(self.api.get_notes()) == note_count - 1,
            message=f"Deleting note by {way} failed.",
        )
