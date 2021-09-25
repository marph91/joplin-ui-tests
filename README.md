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
