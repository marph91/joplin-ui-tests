# joplin-ui-tests

[![ui-tests](https://github.com/marph91/joplin-ui-tests/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/marph91/joplin-ui-tests/actions/workflows/ui-tests.yml)

System tests for the [joplin](https://joplinapp.org/) desktop application in python.

## Motivation

Main motivation is to learn how an electron app can be tested with selenium.

## Requirements

Example for ubuntu 20.04:

```bash
sudo apt install ffmpeg xvfb
pip install -r requirements.txt
```

## Test Overview

### What is tested?

All tests of the following table are successfully executed, except of the tests marked with &#9746;.

| Section  | Function / Feature        | By          | Comment                                       |
|----------|---------------------------|-------------|-----------------------------------------------|
| General  | Focus note list           | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Focus note title          | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Focus note body           | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Focus sidebar             | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Go back                   | Top menu    |                                               |
|          | Go forward                | Top menu    |                                               |
|          | Goto anything             | Hotkey      | &#9745; Notebooks &#9746; Tags and notes      |
|          |                           | Top menu    |                                               |
|          | Show app title            | -           |                                               |
|          | Change app layout         | Top menu    | Smoke test                                    |
|          | Toggle sidebar            | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Toggle note list          | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Zoom (in, out, reset)     | Hotkey      |                                               |
|          |                           | Top menu    | &#9746; Slow                                  |
| Editor   | Show note properties      | Button      |                                               |
|          | Toggle layout             | Button      |                                               |
|          |                           | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
| Notelist | Add note                  | Button      |                                               |
|          |                           | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Add todo                  | Button      |                                               |
|          |                           | Hotkey      |                                               |
|          |                           | Top menu    |                                               |
|          | Delete note               | Hotkey      | &#9746; Cause not clear                       |
|          |                           | Right click | &#9746; Cause not clear                       |
|          | Duplicate note            | Right click |                                               |
|          | Switch type (note - todo) | Right click |                                               |
|          | Complete todo             | Click       |                                               |
|          | Get link                  | Right click |                                               |
| Sidebar  | Synchronise button        | Click       | Smoke test                                    |
|          | Add notebook              | Button      |                                               |
|          |                           | Right click |                                               |
|          |                           | Top menu    |                                               |
|          | Add sub notebook          | Right click |                                               |
|          |                           | Top menu    |                                               |
|          | Delete notebook           | Hotkey      | &#9746; Cause not clear                       |
|          |                           | Right click | &#9746; Cause not clear                       |
|          | Rename notebook           | Right click |                                               |
|          | Note count label          | -           | &#9746; Not displayed for long notebook names |
|          | Notebook collapsing       | Click       |                                               |
|          | Show all notes button     | Click       |                                               |
|          | Drag notebook             | Click       | &#9746; Webdriver bug                         |
|          | Export notebook           | Click       | &#9746; Download dialog doesn't work          |
|          | Add tag                   | Bottom bar  |                                               |
|          |                           | Hotkey      |                                               |
|          |                           | Right click |                                               |
|          |                           | Top menu    |                                               |
|          | Delete tag                | Right click | &#9746; Cause not clear                       |
|          | Rename tag                | Right click |                                               |
|          | Tag collapsing            | Click       |                                               |

### What is not tested?

Except of the marked tests in the table above, there are some other untested features:

- Searching: <https://github.com/laurent22/joplin#searching>
- Attachments: <https://github.com/laurent22/joplin#attachments>
- External editor: <https://github.com/laurent22/joplin#external-text-editor>
- Note history: <https://github.com/laurent22/joplin#note-history>
- Encryption: <https://github.com/laurent22/joplin#encryption>
- Synchronisation: <https://github.com/laurent22/joplin#synchronisation>
- Importing: <https://github.com/laurent22/joplin#importing>
- <https://github.com/laurent22/joplin#features>:
  - Sorting notes
  - Alarms
  - Inline display of PDF, video and audio files
  - Geo-location
  - Multiple languages
  - Custom keyboard shortcuts

## Usage

Don't run with your normal joplin profile, since the tests are modifying and deleting the content!

```bash
python run_tests.py
```

## Test structure

The tests are usually structured in the following way:

1. set the preconditions via API
2. do the UI action
3. check the results via API

Single tests are not independent. Only test classes are mostly independent, since that saves much time. The webdriver and xvfb session are shared through all tests.

## Lessons learned

- Don't use language dependent locators. There were several problems, because my system language is german, but at the reference, I used english.
- Recording the full testsuite can be very valuable. For example at the frame by frame playback, it was visible that the top menu did lose focus, because the label count was updated one frame after focussing.
- `find_elements*` is time consuming, since it has to search the full tree. In contrast `find_element*` returns the first found item.
