"""Tests for the editor on the right."""

from datetime import datetime

from parameterized import parameterized
import pyautogui

import base
import menu


class Header(base.Test):
    def test_note_properties(self):
        id_ = self.new_id()
        self.api.add_note(id_=id_)
        note_element = self.driver.find_element_by_xpath(f"//a[@data-id='{id_}']")
        note_element.click()

        current_time_formatted = datetime.now().strftime("%d/%m/%Y %H:%M")
        timelabel = self.editor.find_element_by_class_name("updated-time-label")
        self.assertEqual(timelabel.text, current_time_formatted)

        # avoid language specific locators
        editor_toolbar = self.editor.find_element_by_class_name("editor-toolbar")
        toolbar_buttons = editor_toolbar.find_elements_by_class_name("button")
        toolbar_buttons[-1].click()  # note properties
        try:
            note_properties = self.editor.find_elements_by_xpath(
                "//div[@class='note-property-box']/*[2]"
            )

            self.assertEqual(note_properties[0].text, current_time_formatted)  # created
            self.assertEqual(note_properties[1].text, current_time_formatted)  # updated
            # note_properties[2]  # url
            # note_properties[3]  # location
            # note_properties[4]  # history, language specific
            self.assertEqual(note_properties[5].text, "Markdown")  # markup
            self.assertEqual(note_properties[6].text, id_)  # id
        finally:
            # close the dialog, doesn't matter if ok or cancel
            button = self.editor.find_element_by_xpath(
                "//div[@class='note-property-box']/../..//button"
            )
            button.click()


class Editor(base.Test):
    def toggle_layout(self, way="button"):

        if way == "button":
            editor_toolbar = self.editor.find_element_by_class_name("editor-toolbar")
            toolbar_buttons = editor_toolbar.find_elements_by_class_name("button")
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
        editor = self.editor.find_element_by_xpath(
            "//div[@class='codeMirrorEditor']/.."
        )
        viewer = self.editor.find_element_by_xpath(
            "//iframe[@class='noteTextViewer']/.."
        )

        def viewer_is_displayed():
            return not "max-width: 1px" in viewer.get_attribute("style")

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
