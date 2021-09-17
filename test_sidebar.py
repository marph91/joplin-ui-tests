"""Tests for the sidebar on the left."""

import random

import base


class Sidebar(base.Test):
    def test_create_notebook(self):
        # TODO: check for correct name

        for way in ("button", "right_click", "top_menu"):
            with self.subTest(way=way):
                notebook_count = len(self.get_notebooks())
                self.add_notebook(way=way)
                self.wait_for(
                    lambda: len(self.get_notebooks()) == notebook_count + 1,
                    message=f"Adding notebook by {way} failed.",
                )

    def test_create_sub_notebook(self):
        # TODO: check for correct name
        # TODO: check for correct place (parent element)

        for way in ("right_click", "top_menu"):
            with self.subTest(way=way):
                notebooks = self.get_notebooks()
                parent_notebook = random.choice(notebooks)

                self.add_notebook(way=way, parent=parent_notebook)
                self.wait_for(
                    lambda: len(self.get_notebooks()) == len(notebooks) + 1,
                    message=f"Adding notebook by {way} failed.",
                )

    def test_notebook_collapsing(self):
        self.assertTrue(self.notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertFalse(self.notebooks_div.is_displayed())
        self.notebooks_title.click()
        self.assertTrue(self.notebooks_div.is_displayed())

    def test_show_all_notes(self):
        # TODO: Doesn't work for many notes or small window.

        all_notes_button = self.notebooks_div.find_element_by_class_name("all-notes")
        all_notes_button.click()

        note_counts = self.notebooks_div.find_elements_by_class_name("note-count-label")
        total_note_count = sum([int(c.text) for c in note_counts])

        self.assertEqual(len(self.get_notes()), total_note_count)

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
