"""Tests for the notelist in the center."""

import itertools
import logging
import time

from parameterized import parameterized
import pyautogui
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import base
import menu


class Note(base.Test):
    note = None
    note_id = None
    notebook = None
    notebook_id = None

    def setUp(self):
        super().setUp()
        if self.__class__.note is None:
            (
                self.__class__.note,
                self.__class__.note_id,
                self.__class__.notebook,
                self.__class__.notebook_id,
            ) = self.select_random_note()

    def add_note(
        self,
        way: str = "button",
        title: str = "test_title",
        content: str = "test_content",
        todo: bool = False,
    ):
        logging.debug(f"UI: add note {title=}")

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
    def test_add(self, type_, way):
        note_count = len(self.api.get_notes(parent_id=self.notebook_id))
        self.add_note(title=self._testMethodName, way=way, todo=type_ == "todo")
        self.wait_for(
            lambda: len(self.api.get_notes(self.notebook_id)) == note_count + 1,
            message=f"Adding note by {way} failed.",
        )

    @parameterized.expand(("hotkey", "right_click"))
    def test_delete_note(self, way):
        self.skipTest("TODO: Running this test causes multiple tests to fail.")
        # TODO: check if correct note got deleted

        note_element, _, _, _ = self.select_random_note(exclude=[self.note_id])
        note_count = len(self.api.get_notes())
        self.delete_note(note_element, way=way)
        self.wait_for(
            lambda: len(self.api.get_notes()) == note_count - 1,
            message=f"Deleting note by {way} failed.",
        )

    def test_duplicate_note(self):
        note_count = len(self.api.get_notes())

        # duplicate by right click
        ActionChains(self.driver).context_click(self.note).perform()
        menu.choose_entry(3)

        self.wait_for(
            lambda: len(self.api.get_notes()) == note_count + 1,
            message="Duplicating note by right click failed.",
        )

        notes = self.api.get_notes(query={"fields": "parent_id,title,body"})
        duplicated_notes = [
            note for note in notes if note["title"].startswith(self.note.text)
        ]
        self.assertEqual(len(duplicated_notes), 2)
        self.assertEqual(
            duplicated_notes[0]["parent_id"], duplicated_notes[1]["parent_id"]
        )
        self.assertEqual(duplicated_notes[0]["body"], duplicated_notes[1]["body"])

    def test_switch_type(self):
        def switch_type():
            # switch by right click
            ActionChains(self.driver).context_click(self.note).perform()
            menu.choose_entry(5)

        def is_todo():
            return bool(
                self.api.get_note(id_=self.note_id, query={"fields": "is_todo"})[
                    "is_todo"
                ]
            )

        initial = is_todo()
        switch_type()
        self.assertNotEqual(initial, is_todo())
        switch_type()
        self.assertEqual(initial, is_todo())

    def test_complete_todo(self):
        id_ = self.new_id()
        self.api.add_note(self._testMethodName, id_=id_, todo=True)
        todo_checkbox = self.find_element_present(
            By.XPATH, f"//a[@data-id='{id_}']/..//input"
        )

        def todo_completed():
            return self.api.get_note(id_=id_, query={"fields": "todo_completed"})[
                "todo_completed"
            ]

        self.assertEqual(todo_completed(), 0)
        t_start = time.time() * 1000  # ms
        todo_checkbox.click()
        t_end = time.time() * 1000  # ms
        t_completed_api = todo_completed()
        self.assertGreaterEqual(t_completed_api, t_start)
        self.assertLessEqual(t_completed_api, t_end)
        todo_checkbox.click()
        self.assertEqual(todo_completed(), 0)

    def test_markdown_link(self):
        # get link by right click
        ActionChains(self.driver).context_click(self.note).perform()
        menu.choose_entry(6)

        self.assertEqual(f"[{self.note.text}](:/{self.note_id})", pyperclip.paste())
