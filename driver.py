"""
Helper module to load and start the chromedriver only once,
even when used in multiple modules.
"""

import io
import os
import shutil
import stat
import zipfile

import requests
from selenium import webdriver


def download_chromedriver(destination: str = "./bin/chromedriver"):
    """
    Electron app uses chrome 85.0.4183.121. Download the corresponding chromedriver.
    How to obtain the correct chromedriver version for an electron app:
    1. Get electron version from projects "package.json".
    2. Check the electron-chrome mapping:
       https://github.com/electron/electron/blob/v14.0.0/DEPS
    3. Download chromedriver:
       https://chromedriver.chromium.org/downloads
    """
    if not os.path.exists(destination):
        response = requests.get(
            "https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip"  # pylint: disable=line-too-long
        )
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as chromedriver_zip:
            chromedriver_zip.extract("chromedriver", path=".")
    if not os.access(destination, os.X_OK):
        # readd the executable flag
        os.chmod(destination, os.stat(destination).st_mode | stat.S_IEXEC)
    return destination


def download_joplin(destination: str = "./bin/joplin.AppImage"):
    if not os.path.exists(destination):
        # TODO: How to download the latest release?
        response = requests.get(
            "https://github.com/laurent22/joplin/releases/download/v2.4.7/Joplin-2.4.7.AppImage"  # pylint: disable=line-too-long
        )
        response.raise_for_status()
        with open(destination, "wb") as outfile:
            outfile.write(response.content)
    if not os.access(destination, os.X_OK):
        # readd the executable flag
        os.chmod(destination, os.stat(destination).st_mode | stat.S_IEXEC)
    return destination


chromedriver_service = webdriver.chrome.service.Service(download_chromedriver())
chromedriver_service.start()

# delete previous profile and start with a fresh one
shutil.rmtree("--remote-debugging-port=0", ignore_errors=True)

# https://www.selenium.dev/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html#module-selenium.webdriver.remote.webdriver
driver = webdriver.remote.webdriver.WebDriver(
    command_executor=chromedriver_service.service_url,
    desired_capabilities={
        "goog:chromeOptions": {
            "binary": download_joplin(),
            # TODO: How to forward a correct profile to the app through webdriver?
            # https://stackoverflow.com/q/69180856/7410886
            "args": ["--profile", "--no-welcome"],
            # needed to avoid "unknown flag" errors
            # https://stackoverflow.com/a/51350140/7410886
            # https://source.chromium.org/chromium/chromium/src/+/main:chrome/test/chromedriver/chrome_launcher.cc;l=188
            "excludeSwitches": [
                "disable-background-networking",
                "disable-client-side-phishing-detection",
                "disable-default-apps",
                "disable-hang-monitor",
                "disable-popup-blocking",
                "disable-prompt-on-repost",
                "disable-sync",
                "enable-automation",
                "enable-blink-features",
                "log-level",
                "no-first-run",
                "no-service-autorun",
                "password-store",
                "test-type",
                "use-mock-keychain",
                "user-data-dir",
            ],
        },
    },
)

# TODO: How to properly download/export?
# https://stackoverflow.com/a/40656336/7410886
# options = webdriver.ChromeOptions()
# options.add_experimental_option(
#    "prefs",
#    {
#        "download.default_directory": "~/tmp",
#        "download.prompt_for_download": False,
#        "download.directory_upgrade": True,
#        "safebrowsing.enabled": True,
#    },
# )
