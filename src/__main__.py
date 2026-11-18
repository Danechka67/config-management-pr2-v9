"""Точка входа для вывода прямых зависимостей."""

import sys
import tarfile

from src.apk import exact_package, load_index
from src.config import options


def main():
    """Получить точную версию и напечатать её требования."""
    args = options()
    try:
        if args.test == "1":
            raise ValueError("тестовый граф появится на этапе 3")
        package = exact_package(load_index(args.repo), args.package,
                                args.version)
        print("\n".join(package.dependencies) or "Зависимостей нет")
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
