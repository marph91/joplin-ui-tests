"""Tests for the sidebar on the left."""

from parameterized import parameterized
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import base
import menu


class Sidebar(base.Test):
    def add_notebook(self, name: str = "test", way: str = "button", parent=None):

        if way == "button":
            add_notebook_button = self.sidebar.find_element_by_xpath(
                "//div[@data-folder-id]/following-sibling::button"
            )
            add_notebook_button.click()
        elif way == "right_click":
            if parent is None:
                # right click on the notebooks title at top
                notebook_title = self.driver.find_element_by_xpath(
                    "//div[@data-folder-id]"
                )

                # first option of dropdown
                # TODO: Find a way to abstract all menus.
                ActionChains(self.driver).context_click(notebook_title).perform()
                menu.choose_entry(1)
            else:
                # right click on the specified parent notebook
                ActionChains(self.driver).context_click(parent).perform()
                menu.choose_entry(1)  # first option of dropdown
        elif way == "top_menu":
            if parent is None:
                menu.top(["File", "New notebook"])
            else:
                parent.click()
                self.wait_for(lambda: "selected" in parent.get_attribute("class"))
                menu.top(["File", "New sub-notebook"])
        else:
            ValueError("Not supported")

        add_notebook_dialog = self.driver.find_element_by_class_name("modal-layer")
        self.wait_for(add_notebook_dialog.is_displayed)
        notebook_title_input = add_notebook_dialog.find_element_by_tag_name("input")
        notebook_title_input.send_keys(name)
        add_notebook_buttons = add_notebook_dialog.find_elements_by_tag_name("button")

        [b for b in add_notebook_buttons if b.text == "OK"][0].click()

    def delete_notebook(self, element):
        # Notebooks are only deletable by right click.

        # second option of dropdown
        # TODO: Find a way to abstract all menus.
        ActionChains(self.driver).context_click(element).perform()
        menu.choose_entry(2)

        # left button to confirm
        # TODO: Selectable via webdriver?
        # TODO: Why are two clicks necessary?
        menu.choose_entry(2, key="left")

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
