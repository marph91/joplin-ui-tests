"""Tests for the notelist in the center."""

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

        # Check the notecount next to the selected notebook, because this works for small windows and many notes.
        notebooks = self.get_notebooks()
        selected_notebook = [
            n for n in notebooks if "selected" in n.get_attribute("class")
        ][0]

        for way in ("button", "hotkey", "top_menu"):
            with self.subTest(way=way):
                note_count = self.get_note_count(selected_notebook)
                self.add_note(way=way)
                self.wait_for(
                    lambda: self.get_note_count(selected_notebook) == note_count + 1,
                    message=f"Adding note by {way} failed.",
                )

    def test_create_todo(self):

        # Check the notecount next to the selected notebook, because this works for small windows and many notes.
        notebooks = self.get_notebooks()
        selected_notebook = [
            n for n in notebooks if "selected" in n.get_attribute("class")
        ][0]

        for way in ("button", "hotkey", "top_menu"):
            with self.subTest(way=way):
                note_count = self.get_note_count(selected_notebook)
                self.add_todo(way=way)
                self.wait_for(
                    lambda: self.get_note_count(selected_notebook) == note_count + 1,
                    message=f"Adding todo by {way} failed.",
                )
