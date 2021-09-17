"""Tests for the notelist in the center."""

import base


class Notelist(base.Test):
    def test_create_note(self):

        # Check the notecount next to the selected notebook, because this works for small windows and many notes.
        notebooks = self.get_notebooks()
        selected_notebook = [
            n for n in notebooks if "selected" in n.get_attribute("class")
        ][0]

        def get_note_count():
            return int(
                selected_notebook.find_element_by_class_name("note-count-label").text
            )

        for way in ("button", "hotkey", "top_menu"):
            with self.subTest(way=way):
                note_count = get_note_count()
                print(note_count)
                self.add_note(way=way)
                self.wait_for(
                    lambda: get_note_count() == note_count + 1,
                    message=f"Adding note by {way} failed.",
                )

