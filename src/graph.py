"""Граф зависимостей и обход без рекурсии."""

from collections import defaultdict, deque
from pathlib import Path

from src.config import LETTER
from src.versions import matches, split


def read_fixture(source, version):
    """Прочитать строки «A: B C» и проверить все ссылки."""
    graph = {}
    for number, line in enumerate(Path(source).read_text().splitlines(), 1):
        if not line.strip():
            continue
        name, targets = fixture_entry(line, number)
        if name in graph:
            raise ValueError(f"строка {number}: повтор пакета {name}")
        graph[name] = targets
    referenced = {item for targets in graph.values() for item in targets}
    missing = referenced - graph.keys()
    if missing:
        raise ValueError(f"нет записей: {', '.join(sorted(missing))}")
    return {f"{key}@{version}": tuple(f"{item}@{version}" for item in values)
            for key, values in graph.items()}


def fixture_entry(line, number):
    """Разобрать одну строку графа."""
    left, colon, right = line.partition(":")
    name, targets = left.strip(), tuple(dict.fromkeys(right.split()))
    if not colon or any(not LETTER.fullmatch(item)
                        for item in (name, *targets)):
        raise ValueError(f"строка {number}: ожидается A: B C")
    return name, targets


def package_id(package):
    """Показать имя и версию как идентификатор вершины."""
    return f"{package.name}@{package.version}"


def providers(packages):
    """Построить индекс имён и виртуальных возможностей."""
    result = defaultdict(list)
    for package in packages:
        result[package.name].append((package.version, package_id(package)))
        for alias in package.provides:
            name, _, version = split(alias)
            result[name].append((version, package_id(package)))
    return result


def neighbors(requirements, index):
    """Найти кандидатов. Оставить отметку о неразрешённых требованиях."""
    result = {}
    for requirement in requirements:
        if requirement.startswith("!"):
            continue
        name, op, version = split(requirement)
        choices = [key for actual, key in index.get(name, ())
                   if matches(actual, op, version)]
        for key in choices or [f"? {requirement}"]:
            result[key] = None
    return tuple(result)


def apk_graph(packages):
    """Построить список смежности для записей одного индекса."""
    index = providers(packages)
    return {package_id(pkg): neighbors(pkg.dependencies, index)
            for pkg in packages}


def bfs(graph, root, excluded=""):
    """Сохранить рёбра и посетить каждую доступную вершину один раз."""
    queue, seen, result = deque([root]), {root}, {}
    while queue:
        node = queue.popleft()
        targets = tuple(child for child in graph.get(node, ())
                        if not excluded or excluded not in name_of(child))
        result[node] = targets
        for child in targets:
            if child not in seen:
                queue.append(child)
                seen.add(child)
    return result


def name_of(node):
    """Вернуть имя без версии или имя неразрешённого требования."""
    if node.startswith("? "):
        return split(node.removeprefix("? "))[0]
    return node.split("@", 1)[0]
