"""Точка входа прототипа."""

from src.config import options


def main():
    """Вывести все параметры."""
    for name, value in vars(options()).items():
        print(f"{name}={value}")


if __name__ == "__main__":
    main()
