"""Utilities to interact with the API."""

import logging
import time
from typing import Optional

from joppy.api import Api
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver import driver
import menu

# Wait until an element has loaded to continue.
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "rli-sideBar"))
)

# activate the api if not already done
menu.top(["Tools", "Options"])
web_clipper_tab = driver.find_element_by_xpath("//a/span[text()='Web Clipper']")
web_clipper_tab.click()
api = Api(driver.find_element_by_xpath("//span[string-length(text())=128]").text)

# avoid any language specific locators
buttons = driver.find_elements_by_tag_name("button")
try:
    api.ping()
except requests.exceptions.ConnectionError:
    buttons[0].click()  # activate button

# try three times until the API is available
for i in range(3):
    try:
        logging.debug(f"API: ping, try {i + 1}")
        api.ping()
        break
    except requests.exceptions.ConnectionError:
        # try another time
        time.sleep(0.1)
api.ping()
logging.debug("API: ping successful")

buttons[-1].click()  # back button
