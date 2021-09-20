"""General test cases."""

import base


class General(base.Test):
    def test_app_title(self):
        self.assertEqual(self.driver.title, "Joplin")
