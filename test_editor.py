"""Tests for the editor on the right."""

from datetime import datetime, timedelta

from parameterized import parameterized
import pyautogui
from selenium.webdriver.common.by import By

import base
import menu


class Header(base.Test):
    notebook = None

    def setUp(self):
        super().setUp()
        # Ensure the notebook is selected, in order to find the created note in the UI.
        if self.__class__.notebook is None:
            self.__class__.notebook, _ = self.select_random_notebook()

    def test_note_properties(self):
        def get_note_properties():
            return self.editor.find_elements(
                By.XPATH, "//div[@class='note-property-box']/*[2]"
            )

        id_ = self.new_id()
        self.api.add_note(title=self._testMethodName, id_=id_)
        note_element = self.find_element_present(By.XPATH, f"//a[@data-id='{id_}']")
        note_element.click()

        # Also consider one minute in the past, since there is a little time difference.
        valid_dates = (
            (datetime.now() - timedelta(minutes=1)).strftime("%d/%m/%Y %H:%M"),
            datetime.now().strftime("%d/%m/%Y %H:%M"),
        )
        timelabel = self.editor.find_element(By.CLASS_NAME, "updated-time-label")
        self.assertIn(timelabel.text, valid_dates)

        # avoid language specific locators
        editor_toolbar = self.editor.find_element(By.CLASS_NAME, "editor-toolbar")
        toolbar_buttons = editor_toolbar.find_elements(By.CLASS_NAME, "button")
        toolbar_buttons[-1].click()  # note properties
        try:
            note_properties = get_note_properties()
            if note_properties == []:
                # Try again, because the window can be empty at first try.
                note_properties = get_note_properties()

            self.assertIn(note_properties[0].text, valid_dates)  # created
            self.assertIn(note_properties[1].text, valid_dates)  # updated
            # note_properties[2]  # url
            # note_properties[3]  # location
            # note_properties[4]  # history, language specific
            self.assertEqual(note_properties[5].text, "Markdown")  # markup
            self.assertEqual(note_properties[6].text, id_)  # id
        finally:
            # close the dialog, doesn't matter if ok or cancel
            button = self.editor.find_element(
                By.XPATH, "//div[@class='note-property-box']/../..//button"
            )
            button.click()


class Editor(base.Test):
    note = None

    def setUp(self):
        super().setUp()
        # Ensure a note is selected, because only then the editor is visible.
        if self.__class__.note is None:
            self.__class__.note, _, _, _ = self.select_random_note()

    def toggle_layout(self, way="button"):
        if way == "button":
            editor_toolbar = self.editor.find_element(By.CLASS_NAME, "editor-toolbar")
            toolbar_buttons = editor_toolbar.find_elements(By.CLASS_NAME, "button")
            toggle_layout_button = toolbar_buttons[2]
            toggle_layout_button.click()
        elif way == "hotkey":
            pyautogui.hotkey("ctrl", "l")
        elif way == "top_menu":
            menu.top(["View", "Toggle editor layout"])
        else:
            ValueError("Not supported")

    @parameterized.expand(("button", "hotkey", "top_menu"))
    def test_toggle_layout(self, way):
        editor = self.editor.find_element(
            By.XPATH, "//div[@class='codeMirrorEditor']/.."
        )
        viewer = self.editor.find_element(
            By.XPATH, "//iframe[@class='noteTextViewer']/.."
        )

        def viewer_is_displayed():
            return "max-width: 1px" not in viewer.get_attribute("style")

        self.assertTrue(editor.is_displayed())
        self.assertTrue(viewer_is_displayed())
        self.toggle_layout(way=way)
        self.assertTrue(editor.is_displayed())
        self.assertFalse(viewer_is_displayed())
        self.toggle_layout(way=way)
        self.assertFalse(editor.is_displayed())
        self.assertTrue(viewer_is_displayed())
        self.toggle_layout(way=way)
        self.assertTrue(editor.is_displayed())
        self.assertTrue(viewer_is_displayed())
