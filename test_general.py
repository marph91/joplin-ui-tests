"""General test cases."""

import enum

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


class General(base.Test):
    def test_app_title(self):
        self.assertEqual(self.driver.title, "Joplin")

    @parameterized.expand(("hotkey", "top_menu"))
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
