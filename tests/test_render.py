"""Проверки результата визуализации через CLI."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from PIL import Image


class RenderTests(unittest.TestCase):
    """Визуализация цикла с повторной ссылкой."""

    def test_cli_renders_cycle(self):
        """CLI сохраняет PNG и Mermaid и завершает вывод дерева."""
        with TemporaryDirectory() as directory:
            output = Path(directory) / "cycle.png"
            result = subprocess.run(
                [sys.executable, "-m", "src", "--test", "1",
                 "--repo", "examples/cycle.txt", "--package", "A",
                 "--version", "1", "--ascii", "1", "--output", str(output)],
                capture_output=True, text=True, check=True,
            )
            with Image.open(output) as image:
                self.assertEqual(image.format, "PNG")
                image.verify()
            diagram = output.with_suffix(".mmd").read_text()
            self.assertIn("n2 --> n0", diagram)
            self.assertIn("A@1 [уже показан]", result.stdout)
