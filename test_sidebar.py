"""Tests for the sidebar on the left."""

from parameterized import parameterized
from selenium.common.exceptions import NoSuchElementException

import base


class Sidebar(base.Test):
    @parameterized.expand(("button", "right_click", "top_menu"))
    def test_create_notebook(self, way):
        # TODO: check for correct name

        notebook_count = len(self.api.get_notebooks())
        self.add_notebook(way=way)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count + 1,
            message=f"Adding notebook by {way} failed.",
        )

    @parameterized.expand(("right_click", "top_menu"))
    def test_create_sub_notebook(self, way):
        # TODO: check for correct name
        # TODO: check for correct place (parent element)

        notebook_element, _ = self.select_random_notebook()

        notebook_count = len(self.api.get_notebooks())
        self.add_notebook(way=way, parent=notebook_element)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count + 1,
            message=f"Adding notebook by {way} failed.",
        )

    def test_delete_notebook(self):
        self.skipTest("TODO: Only works as a single test.")
        # TODO: check if correct notebook got deleted

        # Create a dummy notebook to keep the count constant.
        self.api.add_notebook()

        notebook_element, _ = self.select_random_notebook()
        notebook_count = len(self.api.get_notebooks())
        self.delete_notebook(notebook_element)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count - 1,
            message="Deleting notebook by right click failed.",
        )

    # TODO: Why does it only work in this order and as single tests?
    @parameterized.expand(("right_click", "hotkey"))
    def test_delete_note(self, way):
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

    def test_note_count_label(self):
        def get_note_count_by_label(notebook) -> int:
            try:
                actual = int(
                    notebook.find_element_by_class_name("note-count-label").text
                )
            except NoSuchElementException:
                actual = 0
            return actual

        # Add empty notebook to have at least two notebooks.
        # One with notes and one without notes.
        self.api.add_notebook()
        notebooks = self.get_notebooks()
        for notebook in notebooks:
            # Sometimes the note count needs time to update.
            self.wait_for(
                lambda: len(
                    self.api.get_notes(notebook.get_attribute("data-folder-id"))
                )
                == get_note_count_by_label(notebook),
                timeout=3,
            )

    def test_notebook_collapsing(self):
        self.assertTrue(self.notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertFalse(self.notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertTrue(self.notebooks_div.is_displayed())

    def test_show_all_notes(self):
        all_notes_button = self.notebooks_div.find_element_by_class_name("all-notes")
        all_notes_button.click()
        self.assertEqual(len(self.get_notes()), len(self.api.get_notes()))

    def test_tags(self):
        # TODO: extend
        self.sidebar.find_element_by_xpath("//div/i[contains(@class, 'icon-tags')]")

    def test_drag_notebooks(self):
        self.skipTest("Drag and drop doesn't seem to work yet.")
        # https://github.com/webdriverio/webdriverio/issues/4134
        # ActionChains(self.driver).drag_and_drop(
        #    self.get_notebooks()[0], self.get_notebooks()[1]
        # ).perform()

    def test_synchronise_button(self):
        # TODO: extend
        self.sidebar.find_element_by_xpath(
            "//button/span[contains(@class, 'icon-sync')]"
        )

    def test_export_notebook(self):
        self.skipTest("Download dialog doesn't work yet.")
        for _ in ("JEX", "RAW", "MD", "HTML (File)", "HTML (Directory)"):
            pass
