"""Загрузка источника и обход зависимостей."""

import sys
import tarfile

from src.apk import exact_package, load_index
from src.config import options
from src.graph import apk_graph, bfs, package_id, read_fixture, reverse


def load(args):
    """Выбрать APKINDEX или тестовый файл и проверить корень."""
    root = f"{args.package}@{args.version}"
    if args.test == "1":
        graph = read_fixture(args.repo, args.version)
        if root not in graph:
            raise ValueError(f"пакет {args.package} отсутствует")
        return graph, root
    packages = load_index(args.repo)
    package = exact_package(packages, args.package, args.version)
    return apk_graph(packages), package_id(package)


def main():
    """Вывести достижимый граф."""
    args = options()
    try:
        graph, root = load(args)
        for node, targets in bfs(reverse(graph), root, args.filter).items():
            print(f"{node}: {' '.join(targets)}")
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
