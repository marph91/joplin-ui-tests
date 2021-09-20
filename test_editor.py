"""Tests for the editor on the right."""

from datetime import datetime

import base


class Header(base.Test):
    def test_note_properties(self):
        id_ = self.new_id()
        self.api.add_note(id_=id_)
        note_element = self.driver.find_element_by_xpath(f"//a[@data-id='{id_}']")
        note_element.click()

        current_time_formatted = datetime.now().strftime("%d/%m/%Y %H:%M")
        timelabel = self.editor.find_element_by_class_name("updated-time-label")
        self.assertEqual(timelabel.text, current_time_formatted)

        try:
            # avoid language specific locators
            toolbar_buttons = self.editor_toolbar.find_elements_by_class_name("button")
            toolbar_buttons[-1].click()  # note properties

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
