"""Параметры командной строки и проверка ввода."""

import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit

PACKAGE = re.compile(r"[A-Za-z0-9][A-Za-z0-9+_.-]*")
VERSION = re.compile(r"[0-9][A-Za-z0-9+_.-]*")
LETTER = re.compile(r"[A-Z]")
MODES = ("0", "1")


def options(argv=None):
    """Прочитать настройки либо завершиться с ошибкой использования."""
    parser = argparse.ArgumentParser(description="Граф зависимостей Alpine")
    parser.add_argument("--package", required=True, help="имя пакета")
    parser.add_argument("--repo", required=True, help="URL или файл графа")
    parser.add_argument("--test", choices=MODES, default="0")
    parser.add_argument("--version", required=True, help="точная версия")
    parser.add_argument("--output", default="graph.png", type=Path)
    parser.add_argument("--ascii", choices=MODES, default="0")
    parser.add_argument("--filter", default="")
    args = parser.parse_args(argv)
    validate(args, parser)
    return args


def validate(args, parser):
    """Проверить формат имени, версии, источника и результата."""
    pattern = LETTER if args.test == "1" else PACKAGE
    if not pattern.fullmatch(args.package):
        parser.error("--package: неверное имя пакета")
    if not VERSION.fullmatch(args.version):
        parser.error("--version: неверный формат версии")
    if args.output.suffix.lower() != ".png" or args.output.is_dir():
        parser.error("--output: требуется путь к PNG-файлу")
    if any(char.isspace() or not char.isprintable() for char in args.filter):
        parser.error("--filter: пробельные и управляющие символы запрещены")
    validate_source(args, parser)


def validate_source(args, parser):
    """Проверить файл тестового графа или URL индекса."""
    if args.test == "1":
        if not Path(args.repo).is_file():
            parser.error("--repo: файл тестового графа не найден")
    elif not valid_url(args.repo):
        parser.error("--repo: требуется URL HTTP(S)")


def valid_url(source):
    """Проверить, что URL содержит допустимые схему и адрес."""
    try:
        url = urlsplit(source)
        port = url.port
    except ValueError:
        return False
    scheme_ok = url.scheme in {"http", "https"}
    authority_ok = bool(url.hostname and (port is None or port))
    details = (url.username, url.password, url.fragment, url.query)
    simple_url = all(value in (None, "") for value in details)
    return (scheme_ok and authority_ok and simple_url
            and not any(char.isspace() for char in source))
