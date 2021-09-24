"""Tests for the sidebar on the left."""

import logging

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
    note = None
    notebook = None
    notebook_id = None

    def setUp(self):
        super().setUp()
        if self.__class__.note is None:
            (
                self.__class__.note,
                _,
                self.__class__.notebook,
                self.__class__.notebook_id,
            ) = self.select_random_note()

    def add_notebook(self, name: str = "test", way: str = "button", parent=None):
        logging.debug(f"UI: add notebook {name=}, {way=}")

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
        logging.debug("UI: delete notebook")
        # Notebooks are only deletable by right click.

        # second option of dropdown
        # TODO: Find a way to abstract all menus.
        ActionChains(self.driver).context_click(element).perform()
        menu.choose_entry(2)

        # left button to confirm
        menu.choose_entry(1, key="left")

    @parameterized.expand(("button", "right_click", "top_menu"))
    def test_add_notebook(self, way):
        # TODO: check for correct name

        notebook_count = len(self.api.get_notebooks())
        self.add_notebook(name=self._testMethodName, way=way)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count + 1,
            message=f"Adding notebook by {way} failed.",
        )

    @parameterized.expand(("right_click", "top_menu"))
    def test_add_sub_notebook(self, way):
        # TODO: check for correct name
        # TODO: check for correct place (parent element)

        notebook_count = len(self.api.get_notebooks())
        self.add_notebook(name=self._testMethodName, way=way, parent=self.notebook)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count + 1,
            message=f"Adding notebook by {way} failed.",
        )

    def test_delete_notebook(self):
        self.skipTest("TODO: Running this test causes multiple tests to fail.")
        # TODO: check if correct notebook got deleted

        notebook_element, _ = self.select_random_notebook(exclude=[self.notebook_id])
        notebook_count = len(self.api.get_notebooks())
        self.delete_notebook(notebook_element)
        self.wait_for(
            lambda: len(self.api.get_notebooks()) == notebook_count - 1,
            message="Deleting notebook by right click failed.",
        )

    def test_rename_notebook(self):
        # Notebooks are only renamable by right click.
        new_name = self._testMethodName

        # rename notebook via UI
        ActionChains(self.driver).context_click(self.notebook).perform()
        menu.choose_entry(3)
        self.fill_modal_dialog(new_name)

        # check against API reference
        notebooks = self.api.get_notebooks()
        renamed_notebook = [
            notebook for notebook in notebooks if notebook["id"] == self.notebook_id
        ][0]
        self.assertEqual(renamed_notebook["title"], new_name)

    def test_note_count_label(self):
        self.skipTest("TODO: Resizing doesn't work. Is there a reliable way?")
        # Resize the sidebar to make all labels visible.
        sidebar_resize = self.sidebar.find_element_by_xpath(
            "//div[contains(@style, 'col-resize')]"
        )
        ActionChains(self.driver).click_and_hold(sidebar_resize).move_by_offset(
            100, 0
        ).perform()

        def get_note_count_by_label(notebook) -> int:
            try:
                note_label = notebook.find_element_by_class_name("note-count-label")
                self.assertTrue(note_label.is_displayed())
                actual = int(note_label.text)
            except (NoSuchElementException, ValueError):
                actual = 0
            return actual

        # Add a note to have at least one notebook with content.
        self.api.add_note(name=self._testMethodName)
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
        notebooks_div = self.sidebar.find_element_by_xpath(
            "//div[starts-with(@class, 'folders')]"
        )
        self.assertTrue(notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertFalse(notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertTrue(notebooks_div.is_displayed())

    def test_show_all_notes(self):
        all_notes_button = self.sidebar.find_element_by_class_name("all-notes")
        all_notes_button.click()
        self.assertEqual(len(self.get_notes()), len(self.api.get_notes()))

    def test_drag_notebooks(self):
        self.skipTest("Drag and drop doesn't seem to work yet.")
        # doc: https://github.com/laurent22/joplin#sub-notebooks
        # https://github.com/webdriverio/webdriverio/issues/4134
        # ActionChains(self.driver).drag_and_drop(
        #    self.get_notebooks()[0], self.get_notebooks()[1]
        # ).perform()

    def test_export_notebook(self):
        self.skipTest("Download dialog doesn't work yet.")
        # doc: https://github.com/laurent22/joplin#exporting
        for _ in ("JEX", "RAW", "MD", "HTML (File)", "HTML (Directory)"):
            pass


class Tag(base.Test):
    note = None

    def setUp(self):
        super().setUp()
        # Ensure a note is selected. Add all the tags to this note.
        if self.__class__.note is None:
            self.__class__.note, _, _, _ = self.select_random_note()

    def add_tag(self, name: str = "test", way: str = "bottom_bar"):
        logging.debug(f"UI: add tag {name=}, {way=}")

        if way == "bottom_bar":
            bottom_bar = self.editor.find_element_by_xpath("//div[@class='tag-bar']/a")
            bottom_bar.click()
        elif way == "hotkey":
            pyautogui.hotkey("ctrl", "alt", "t")
        elif way == "right_click":
            ActionChains(self.driver).context_click(self.note).perform()
            menu.choose_entry(1)
        elif way == "top_menu":
            menu.top(["Note", "Tags"])
        else:
            ValueError("Not supported")

        self.fill_modal_dialog(name, tag=True)

    @parameterized.expand(("bottom_bar", "hotkey", "right_click", "top_menu"))
    # TODO: Failure caused by late loading of the note label count, which steals
    # the focus while the top menu is accessed. Options:
    # - Repeat the test
    # - Disable the sidepanel
    # - Check if correct element is focussed:
    #   self.is_focussed(
    #       self.driver.find_element_by_xpath("//div[@class='modal-layer']//input"))
    @base.run_again_at_failure
    def test_add_tag(self, way):
        tag_count = len(self.api.get_tags())
        self.add_tag(name=self._testMethodName, way=way)
        self.wait_for(
            lambda: len(self.api.get_tags()) == tag_count + 1,
            message=f"Adding tag by {way} failed.",
        )

    def test_delete_tag(self):
        self.skipTest("TODO: Running this test causes multiple tests to fail.")

        tag_element, _ = self.get_random_tag()
        tag_count = len(self.api.get_tags())

        # delete by right click
        ActionChains(self.driver).context_click(tag_element).perform()
        menu.choose_entry(1)
        menu.choose_entry(1, key="left")

        self.wait_for(
            lambda: len(self.api.get_tags()) == tag_count - 1,
            message="Deleting tag by right click failed.",
        )

    def test_rename_tag(self):
        new_name = self._testMethodName
        tag_element, tag_id = self.get_random_tag()

        # rename by right click
        ActionChains(self.driver).context_click(tag_element).perform()
        menu.choose_entry(2)
        self.fill_modal_dialog(new_name)

        # check against API reference
        tags = self.api.get_tags()
        renamed_tag = [tag for tag in tags if tag["id"] == tag_id][0]
        self.assertEqual(renamed_tag["title"], new_name)

    def test_tag_collapsing(self):
        tag_title = self.sidebar.find_element_by_xpath(
            "//div/i[contains(@class, 'icon-tags')]/.."
        )
        tag_div = self.sidebar.find_element_by_class_name("tags")
        self.assertTrue(tag_div.is_displayed())
        tag_title.click()
        self.assertFalse(tag_div.is_displayed())
        tag_title.click()
        self.assertTrue(tag_div.is_displayed())
