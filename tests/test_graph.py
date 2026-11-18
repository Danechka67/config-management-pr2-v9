"""Проверки графа и обработки особых рёбер."""

import unittest

from src.apk import Package
from src.graph import apk_graph, bfs, read_fixture


class GraphTests(unittest.TestCase):
    """Проверки BFS и построения графа."""

    def test_cycle(self):
        """Цикл сохраняется, обход завершается."""
        graph = read_fixture("examples/cycle.txt", "1")
        result = bfs(graph, "A@1")
        self.assertEqual(list(result), ["A@1", "B@1", "C@1"])
        self.assertEqual(result["C@1"], ("A@1",))

    def test_filter_keeps_shared_child(self):
        """Исключённая вершина не мешает второму пути к общему потомку."""
        graph = read_fixture("examples/diamond.txt", "1")
        self.assertEqual(list(bfs(graph, "A@1", "B")),
                         ["A@1", "C@1", "D@1"])

    def test_provider_constraints(self):
        """Виртуальное имя разрешается с учётом версии провайдера."""
        packages = [
            Package("app", "1", ("so:demo>=2", "!old", "missing"), ()),
            Package("lib", "1", (), ("so:demo=1",)),
            Package("lib", "2", (), ("so:demo=2",)),
        ]
        self.assertEqual(apk_graph(packages)["app@1"],
                         ("lib@2", "? missing"))
