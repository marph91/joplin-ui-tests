"""Custom test runner to provide xvfb and stop the chromedriver."""

import argparse
import contextlib
import logging
import os
import subprocess
import time
import typing
import unittest
import warnings

from xvfbwrapper import Xvfb


@contextlib.contextmanager
def optional(condition: bool, context_manager: typing.ContextManager):
    """
    Execute a context manager conditionally.
    See: https://stackoverflow.com/a/41251962/7410886.
    """
    if condition:
        with context_manager:
            yield
    else:
        yield


class Recording(contextlib.ContextDecorator):
    """Record the complete test run with ffmpeg."""

    def __init__(self, path="debug/output.mp4"):
        super().__init__()
        self.path = path
        self.recording_process = None

    def __enter__(self):
        logging.debug("Start recording")

        # check whether ffmpeg is available
        subprocess.run(
            ["ffmpeg", "--help"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.recording_process = subprocess.Popen(
            # fmt: off
            [
                "ffmpeg",
                "-y",  # overwrite automatically
                "-video_size", "1920x1080",
                "-framerate", "20",
                "-f", "x11grab",
                "-i", os.getenv("DISPLAY"),
                self.path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            # fmt: on
        )
        return self

    def __exit__(self, *exc):
        time.sleep(1)  # give ffmpeg some time to finish
        self.recording_process.terminate()
        self.recording_process.wait()
        return False  # don't suppress exceptions


def configure_logging(debug_dir: str):
    # Don't spam the log. See: https://stackoverflow.com/a/11029841/7410886
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(
        logging.WARNING
    )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.basicConfig(
        filename=f"{debug_dir}/test.log",
        filemode="w",
        format="%(asctime)s [%(levelname)s]: %(message)s",
        level=logging.DEBUG,
    )

    # Suppress RessourceWarning in selenium.
    # See https://github.com/SeleniumHQ/selenium/issues/6878.
    warnings.simplefilter("ignore", ResourceWarning)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug-dir", type=str, default="debug", help="Debug output directory."
    )
    parser.add_argument(
        "--no-xvfb", action="store_true", help="Don't run the tests inside xvfb."
    )
    parser.add_argument(
        "--no-recording", action="store_true", help="Don't record the test run."
    )
    parser.add_argument(
        "--verbosity", type=int, default=2, help="Test runner verbosity."
    )
    parser.add_argument("--testname", help="Run a subset of tests.")
    args = parser.parse_args()
    return args


def run_tests(args):
    os.makedirs(args.debug_dir, exist_ok=True)
    # TODO: Is there a better way to pass the debug dir to the tests?
    os.environ["TEST_DEBUG_DIR"] = args.debug_dir
    with optional(not args.no_xvfb, Xvfb(width=1920, height=1080)), optional(
        not args.no_recording, Recording(path=f"{args.debug_dir}/output.mp4")
    ):
        # The driver should be started in the xvfb context.
        import driver  # pylint: disable=import-outside-toplevel

        try:
            runner = unittest.TextTestRunner(verbosity=args.verbosity)
            if args.testname is None:
                suite = unittest.defaultTestLoader.discover(".")
            else:
                suite = unittest.TestSuite()
                suite.addTests(unittest.TestLoader().loadTestsFromName(args.testname))
            runner.run(suite)
        finally:
            driver.driver.quit()
            driver.chromedriver_service.stop()


def main():
    args = parse_arguments()
    logging.debug(f"CLI arguments: {args}")
    configure_logging(args.debug_dir)
    run_tests(args)


if __name__ == "__main__":
    main()
