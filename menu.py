"""Helper functions for accessing menus of the joplin app."""

import dataclasses
import logging
from typing import Dict, List, Optional, Sequence

import pyautogui


@dataclasses.dataclass
class Entry:
    """Represents an arbitrary menu entry."""

    name: str
    subentries: Sequence = ()


NOTEBOOK_MENU_LAYOUT = (
    Entry("New"),
    Entry("Delete"),
    Entry("Rename"),
    Entry(
        "Export", (Entry("JEX"), Entry("RAW"), Entry("MD"), Entry("HTML"), Entry("PDF"))
    ),
)


# Strings don't have to match the ui exactly, but should still be associable.
TOP_MENU_LAYOUT = (
    Entry(
        "File",
        (
            Entry("New note"),
            Entry("New to-do"),
            Entry("New notebook"),
            Entry("New sub-notebook"),
            Entry(
                "Import",
                (
                    Entry("JEX"),
                    Entry("MD (File)"),
                    Entry("MD (Directory)"),
                    Entry("RAW"),
                    Entry("ENEX (Markdown)"),
                    Entry("ENEX (HTML)"),
                ),
            ),
            Entry(
                "Export all",
                (Entry("JEX"), Entry("RAW"), Entry("MD"), Entry("HTML"), Entry("PDF"),),
            ),
            Entry("Synchronize"),
            Entry("Print"),
            Entry("Quit"),
        ),
    ),
    Entry(
        "Edit",
        (
            Entry("Copy"),
            Entry("Cut"),
            Entry("Paste"),
            Entry("Select all"),
            Entry("Undo"),
            Entry("Redo"),
            Entry("Bold"),
            Entry("Italic"),
            Entry("Hyperlink"),
            Entry("Code"),
            Entry("Insert Date Time"),
            Entry("Attach file"),
            Entry("Delete line"),
            Entry("Duplicate line"),
            Entry("Toggle comment"),
            Entry("Sort selected lines"),
            Entry("Indent less"),
            Entry("Indent more"),
            Entry("Swap line down"),
            Entry("Swap line up"),
            Entry("Search all notes"),
            Entry("Search current note"),
        ),
    ),
    Entry(
        "View",
        (
            Entry("Change application layout"),
            Entry("Toggle sidebar"),
            Entry("Toggle note list"),
            Entry("Toggle editor layout"),
            Entry(
                "Layout button sequence",
                (
                    Entry("Editor / Viewer / Split view"),
                    Entry("Editor / Viewer"),
                    Entry("Editor / Split view"),
                    Entry("Viewer / Split view"),
                ),
            ),
            Entry(
                "Sort notes by",
                (
                    Entry("Updated"),
                    Entry("Created"),
                    Entry("Title"),
                    Entry("Custom"),
                    Entry("Reverse"),
                ),
            ),
            Entry(
                "Sort notebooks by",
                (Entry("Title"), Entry("Updated"), Entry("Reverse")),
            ),
            Entry("Show note counts"),
            Entry("Uncompleted todos on top"),
            Entry("Show completed todos"),
            Entry("Actual size"),
            Entry("Zoom in"),
            Entry("Zoom out"),
        ),
    ),
    Entry(
        "Go",
        (
            Entry("Back"),
            Entry("Forward"),
            Entry(
                "Focus",
                (
                    Entry("Sidebar"),
                    Entry("Note list"),
                    Entry("Note title"),
                    Entry("Note body"),
                ),
            ),
            Entry("Goto anything"),
        ),
    ),
    Entry("Notebook", (Entry("Share"),)),
    Entry(
        "Note",
        (
            Entry("Toggle external editing"),
            Entry("Tags"),
            Entry("Publish note"),
            Entry("Statistics"),
        ),
    ),
    Entry(
        "Tools",
        (
            Entry("Options"),
            Entry("Note attachments"),
            Entry(
                "Spell checker",
                (Entry("Use"), Entry("[Language]"), Entry("Choose language")),
            ),
            Entry("Command palette"),
        ),
    ),
    Entry(
        "Help",
        (
            Entry("Website and docs"),
            Entry("Forum"),
            Entry("Donation"),
            Entry("Updates"),
            Entry("Synchronisation status"),
            Entry("Development tools"),
            Entry("Safe mode"),
            Entry("Open profile directory"),
            Entry("Copy dev mode command"),
            Entry("About"),
        ),
    ),
)


def choose_entry(position: int, key: str = "down", confirm: str = "enter"):
    """Select an entry from an arbitrary menu. The position has to be one based!"""
    pyautogui.press(key, presses=position)
    pyautogui.press(confirm)


def top(path: List[str], skip: Optional[Dict[str, int]] = None):
    """Select an entry from the top menu."""
    # TODO: path gets modified, which can cause side effects

    # skip non selectable entries
    if skip is None:
        skip = {}

    logging.debug(f"Selecting {path} from top menu.")

    pyautogui.press("alt")  # focus the menu

    # find toplevel entry and select it
    toplevel_entry = path.pop(0)
    match_index = [e.name for e in TOP_MENU_LAYOUT].index(toplevel_entry)
    choose_entry(match_index, key="right")
    pyautogui.press("down")  # select the first entry, since match_index is zero based
    last_entry = TOP_MENU_LAYOUT[match_index]

    while path:
        # find next entry and select it
        next_entry = path.pop(0)
        match_index = [e.name for e in last_entry.subentries].index(next_entry)
        choose_entry(match_index - skip.get(next_entry, 0))
        last_entry = last_entry.subentries[match_index]
