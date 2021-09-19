"""Tests for the notelist in the center."""

import itertools

from parameterized import parameterized

import base


class Notelist(base.Test):
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
