"""Tests for the sidebar on the left."""

from parameterized import parameterized
import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import base
import menu


class Sidebar(base.Test):
    def test_synchronise_button(self):
        # TODO: extend
        self.sidebar.find_element_by_xpath(
            "//button/span[contains(@class, 'icon-sync')]"
        )


class Notebook(base.Test):
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

        self.fill_modal_dialog(name)

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
        self.skipTest("TODO: Running this test causes multiple tests to fail.")
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

    def test_rename_notebook(self):
        # Notebooks are only renamable by right click.
        new_name = "abc"
        notebook_element, notebook_id = self.select_random_notebook()

        # rename notebook via UI
        ActionChains(self.driver).context_click(notebook_element).perform()
        menu.choose_entry(3)
        self.fill_modal_dialog(new_name)

        # check against API reference
        notebooks = self.api.get_notebooks()
        renamed_notebook = [
            notebook for notebook in notebooks if notebook["id"] == notebook_id
        ][0]
        self.assertEqual(renamed_notebook["title"], new_name)

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

    def test_drag_notebooks(self):
        self.skipTest("Drag and drop doesn't seem to work yet.")
        # https://github.com/webdriverio/webdriverio/issues/4134
        # ActionChains(self.driver).drag_and_drop(
        #    self.get_notebooks()[0], self.get_notebooks()[1]
        # ).perform()

    def test_export_notebook(self):
        self.skipTest("Download dialog doesn't work yet.")
        for _ in ("JEX", "RAW", "MD", "HTML (File)", "HTML (Directory)"):
            pass


class Tag(base.Test):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure a note is selected. Add all the tags to this note.
        cls.note, _ = cls.select_random_note(cls)

    def add_tag(self, name: str = "test", way: str = "bottom_bar"):
        if way == "bottom_bar":
            bottom_bar = self.editor.find_element_by_xpath("//div[@class='tag-bar']/a")
            bottom_bar.click()
        elif way == "hotkey":
            pyautogui.keyDown("ctrl")
            pyautogui.keyDown("alt")
            pyautogui.press("t")
            pyautogui.keyUp("alt")
            pyautogui.keyUp("ctrl")
        elif way == "right_click":
            ActionChains(self.driver).context_click(self.note).perform()
            menu.choose_entry(1)
        elif way == "top_menu":
            menu.top(["Note", "Tags"])
        else:
            ValueError("Not supported")

        self.fill_modal_dialog(name, tag=True)

    @parameterized.expand(("bottom_bar", "hotkey", "right_click", "top_menu"))
    def test_add_tag(self, way):
        tag_count = len(self.api.get_tags())
        self.add_tag(name=way, way=way)
        self.wait_for(
            lambda: len(self.api.get_tags()) == tag_count + 1,
            message=f"Adding tag by {way} failed.",
        )
