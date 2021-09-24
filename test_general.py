"""General test cases."""

import enum
import itertools
import time

from parameterized import parameterized
import pyautogui

import base
import menu


class Zoom(enum.Enum):
    IN = enum.auto()
    OUT = enum.auto()
    RESET = enum.auto()


ZOOM_MAP = {
    "hotkey": {
        Zoom.IN: lambda: pyautogui.hotkey("ctrl", "shift", "="),
        Zoom.OUT: lambda: pyautogui.hotkey("ctrl", "-"),
        Zoom.RESET: lambda: pyautogui.hotkey("ctrl", "0"),
    },
    "top_menu": {
        Zoom.IN: lambda: menu.top(["View", "Zoom in"]),
        Zoom.OUT: lambda: menu.top(["View", "Zoom out"]),
        Zoom.RESET: lambda: menu.top(["View", "Actual size"]),
    },
}

GOTO_ANYTHING_MAP = {
    "hotkey": lambda: pyautogui.hotkey("ctrl", "p"),
    "top_menu": lambda: menu.top(["Go", "Goto anything"]),
}


# Order is mixed to don't select the same location twice.
FOCUS_MAP = {
    "hotkey": {
        "sidebar": lambda: pyautogui.hotkey("ctrl", "shift", "s"),
        "note_list": lambda: pyautogui.hotkey("ctrl", "shift", "l"),
        "note_title": lambda: pyautogui.hotkey("ctrl", "shift", "n"),
        "note_body": lambda: pyautogui.hotkey("ctrl", "shift", "b"),
    },
    "top_menu": {
        # Skip one entry at the focus selection, because "Forward" is not selectable.
        "sidebar": lambda: menu.top(["Go", "Focus", "Sidebar"], skip={"Focus": 1}),
        "note_list": lambda: menu.top(["Go", "Focus", "Note list"], skip={"Focus": 1}),
        "note_title": lambda: menu.top(
            ["Go", "Focus", "Note title"], skip={"Focus": 1}
        ),
        "note_body": lambda: menu.top(["Go", "Focus", "Note body"], skip={"Focus": 1}),
    },
}


class Go(base.Test):
    notebook = None
    base_element_map = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for key in GOTO_ANYTHING_MAP.keys():
            cls.api.add_note(name=key, content=key)

    def setUp(self):
        super().setUp()
        # Ensure the notebook is selected, in order to select the locations properly.
        if self.__class__.notebook is None:
            self.__class__.notebook, _, _, _ = self.select_random_note()
            self.__class__.base_element_map = {
                "sidebar": self.sidebar,
                "note_list": self.notelist,
                "note_title": self.editor.find_element_by_class_name("title-input"),
                "note_body": self.editor.find_element_by_class_name("codeMirrorEditor"),
            }

    @parameterized.expand(
        itertools.product(FOCUS_MAP.keys(), FOCUS_MAP["hotkey"].keys())
    )
    def test_focus(self, way, location):
        if way == "top_menu":
            self.skipTest("TODO: Non selectable 'forward/back' is not consistent.")
        FOCUS_MAP[way][location]()

        self.assert_contains(
            self.base_element_map[location], self.driver.switch_to.active_element
        )

    def test_go_back_forward(self):
        # All notes should be in the current notebook.
        notes = self.get_notes()
        self.assertEqual(len(notes), 3)

        notes[0].click()
        notes[1].click()
        self.assertNotIn("selected", notes[0].get_attribute("class"))
        self.assertIn("selected", notes[1].get_attribute("class"))

        menu.top(["Go", "Back"])
        self.assertIn("selected", notes[0].get_attribute("class"))
        self.assertNotIn("selected", notes[1].get_attribute("class"))

        menu.top(["Go", "Forward"])
        self.assertNotIn("selected", notes[0].get_attribute("class"))
        self.assertIn("selected", notes[1].get_attribute("class"))

    @parameterized.expand(GOTO_ANYTHING_MAP.keys())
    def test_goto_anything(self, way):
        self.skipTest(
            "TODO: It takes a long time until notes are available at 'goto anything'."
        )
        time.sleep(10)

        GOTO_ANYTHING_MAP[way]()
        # Short waiting time to display the search results.
        self.fill_modal_dialog(way, wait_before_confirm=0.2)

        note_title = self.editor.find_element_by_class_name("title-input")
        self.assertEqual(note_title.get_attribute("value"), way)
        # TODO: strip(), because sometimes an initial space is inserted.
        note_editor = self.editor.find_element_by_class_name("codeMirrorEditor")
        self.assertEqual(note_editor.text.strip(), way)


class View(base.Test):
    def test_app_title(self):
        self.assertEqual(self.driver.title, "Joplin")

    @parameterized.expand(ZOOM_MAP.keys())
    def test_zoom(self, way):
        if way == "top_menu":
            self.skipTest("TODO: Changing zoom by top menu is slow and error prone.")

        def get_sizes():
            return {
                "sidebar": self.sidebar.size,
                "notelist": self.notelist.size,
                "editor": self.editor.size,
            }

        initial_size = get_sizes()

        for _ in range(2):
            ZOOM_MAP[way][Zoom.IN]()
        # Actually only the editor is zooming in x and y direction.
        zoom_in_size = get_sizes()
        # fmt: off
        self.assertLess(zoom_in_size["sidebar"]["height"], initial_size["sidebar"]["height"])
        self.assertEqual(zoom_in_size["sidebar"]["width"], initial_size["sidebar"]["width"])
        self.assertLess(zoom_in_size["notelist"]["height"], initial_size["notelist"]["height"])
        self.assertEqual(zoom_in_size["notelist"]["width"], initial_size["notelist"]["width"])
        self.assertLess(zoom_in_size["editor"]["height"], initial_size["editor"]["height"])
        self.assertLess(zoom_in_size["editor"]["width"], initial_size["editor"]["width"])
        # fmt: on

        for _ in range(4):
            ZOOM_MAP[way][Zoom.OUT]()
        zoom_out_size = get_sizes()
        # fmt: off
        self.assertGreater(zoom_out_size["sidebar"]["height"], initial_size["sidebar"]["height"])
        self.assertEqual(zoom_out_size["sidebar"]["width"], initial_size["sidebar"]["width"])
        self.assertGreater(zoom_out_size["notelist"]["height"], initial_size["notelist"]["height"])
        self.assertEqual(zoom_out_size["notelist"]["width"], initial_size["notelist"]["width"])
        self.assertGreater(zoom_out_size["editor"]["height"], initial_size["editor"]["height"])
        self.assertGreater(zoom_out_size["editor"]["width"], initial_size["editor"]["width"])
        # fmt: on

        ZOOM_MAP[way][Zoom.RESET]()
        self.assertEqual(get_sizes(), initial_size)
