"""Custom test runner to provide xvfb and stop the chromedriver."""

import argparse
import contextlib
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbosity", type=int, default=2, help="Test runner verbosity."
    )
    parser.add_argument(
        "--no-xvfb", action="store_true", help="Don't run the tests inside xvfb."
    )
    parser.add_argument("--testname", help="Run a subset of tests.")
    args = parser.parse_args()

    # Suppress RessourceWarning in selenium.
    # See https://github.com/SeleniumHQ/selenium/issues/6878.
    warnings.simplefilter("ignore", ResourceWarning)

    with optional(not args.no_xvfb, Xvfb(width=1920, height=1080)):
        # The driver should be started in the xvfb context.
        import driver  # pylint: disable=import-outside-toplevel

        runner = unittest.TextTestRunner(verbosity=args.verbosity)
        if args.testname is None:
            suite = unittest.defaultTestLoader.discover(".")
        else:
            suite = unittest.TestSuite()
            suite.addTests(unittest.TestLoader().loadTestsFromName(args.testname))
        runner.run(suite)

    driver.driver.quit()
    driver.chromedriver_service.stop()


if __name__ == "__main__":
    main()
