"""Tests for the notelist in the center."""

import itertools
import random

from parameterized import parameterized

import base


class Notelist(base.Test):
    @parameterized.expand(
        itertools.product(("note", "todo"), ("button", "hotkey", "top_menu"))
    )
    def test_create(self, type_, way):

        notebooks = self.api.get_notebooks()
        notebook_id = random.choice(notebooks)["id"]
        notebook_element = self.driver.find_element_by_xpath(
            f"//div[@data-folder-id='{notebook_id}']"
        )
        notebook_element.click()

        note_count = len(self.api.get_notes(notebook_id))
        self.add_note(way=way, todo=type_ == "todo")
        self.wait_for(
            lambda: len(self.api.get_notes(notebook_id)) == note_count + 1,
            message=f"Adding note by {way} failed.",
        )
