"""Tests for the notelist in the center."""

import random

import base


class Notelist(base.Test):
    def get_note_count(self, notebook):
        label = notebook.find_elements_by_class_name("note-count-label")
        if len(label) == 0:
            return 0
        elif len(label) == 1:
            return int(label[0].text)
        raise ValueError(f"Found too many labels ({len(label)}).")

    def test_create_note(self):

        notebooks = self.api.get_notebooks()
        notebook_id = random.choice(notebooks)["id"]
        notebook_element = self.driver.find_element_by_xpath(
            f"//div[@data-folder-id='{notebook_id}']"
        )
        notebook_element.click()

        for way in ("button", "hotkey", "top_menu"):
            with self.subTest(way=way):
                note_count = len(self.api.get_notes(notebook_id))
                self.add_note(way=way)
                self.wait_for(
                    lambda: len(self.api.get_notes(notebook_id)) == note_count + 1,
                    message=f"Adding note by {way} failed.",
                )

    def test_create_todo(self):

        notebooks = self.api.get_notebooks()
        notebook_id = random.choice(notebooks)["id"]
        notebook_element = self.driver.find_element_by_xpath(
            f"//div[@data-folder-id='{notebook_id}']"
        )
        notebook_element.click()

        for way in ("button", "hotkey", "top_menu"):
            with self.subTest(way=way):
                note_count = len(self.api.get_notes(notebook_id))
                self.add_todo(way=way)
                self.wait_for(
                    lambda: len(self.api.get_notes(notebook_id)) == note_count + 1,
                    message=f"Adding todo by {way} failed.",
                )
