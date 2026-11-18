"""Проверки ошибок всех семи параметров."""

from contextlib import redirect_stderr
from io import StringIO
import unittest

from src.config import options

VALID = {
    "package": "busybox",
    "repo": "https://example.org/main/aarch64",
    "test": "0",
    "version": "1.2-r0",
    "output": "graph.png",
    "ascii": "0",
    "filter": "",
}
INVALID = {
    "package": "a/b",
    "repo": "file:///tmp",
    "test": "2",
    "version": "latest",
    "output": "graph.jpg",
    "ascii": "yes",
    "filter": "a b",
}


def argv(settings):
    """Преобразовать настройки в аргументы."""
    return [part for key, value in settings.items()
            for part in (f"--{key}", value)]


class ConfigTests(unittest.TestCase):
    """Проверки CLI."""

    def test_valid_options(self):
        """Валидная команда сохраняет точную версию."""
        self.assertEqual(options(argv(VALID)).version, "1.2-r0")

    def test_each_invalid_option(self):
        """Каждая опция имеет проверку."""
        for key, value in INVALID.items():
            with self.subTest(key=key), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    options(argv(VALID | {key: value}))
                self.assertEqual(error.exception.code, 2)
