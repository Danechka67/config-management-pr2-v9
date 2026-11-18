"""Чтение записей Alpine и выбор точной версии."""

import unittest

from src.apk import exact_package, parse_index

INDEX = """P:demo
V:1.0-r0
D:lib=1.0-r0 so:libz.so.1 !old
p:cmd:demo=1.0-r0

P:demo
V:2.0-r0
"""


class ApkTests(unittest.TestCase):
    """Проверки чтения индекса."""

    def test_exact_version(self):
        """Зависимости и provides принадлежат выбранной версии."""
        packages = parse_index(INDEX)
        first = exact_package(packages, "demo", "1.0-r0")
        self.assertEqual(first.dependencies,
                         ("lib=1.0-r0", "so:libz.so.1", "!old"))
        self.assertEqual(first.provides, ("cmd:demo=1.0-r0",))
        self.assertEqual(exact_package(packages, "demo", "2.0-r0")
                         .dependencies, ())
        with self.assertRaises(ValueError):
            exact_package(packages, "demo", "3.0-r0")
