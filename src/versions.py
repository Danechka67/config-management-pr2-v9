"""Сопоставление обычных версий и ограничений Alpine."""

import re

CONSTRAINT = re.compile(r"([^<>=~]+)([<>=~]+)?(.*)")
TOKEN = re.compile(r"[0-9]+|[a-z]+")
SUFFIX = {
    "alpha": -4, "beta": -3, "pre": -2, "rc": -1,
    "cvs": 1, "svn": 2, "git": 3, "hg": 4, "p": 5,
}
EQUAL = 0


def split(requirement):
    """Разделить имя, оператор и версию из APKINDEX."""
    match = CONSTRAINT.fullmatch(requirement)
    if not match:
        raise ValueError(f"неверное требование: {requirement}")
    name, operator, version = match.groups()
    return name, operator or "", version


def component(value):
    """Привести токен к ключу сортировки."""
    return (1, int(value)) if value.isdigit() else (0, value)


def version_key(version):
    """Сопоставить основу, суффиксы и номер ревизии."""
    body, separator, revision = version.rpartition("-r")
    if not separator or not revision.isdigit():
        body, revision = version, "0"
    base, *suffixes = body.split("_")
    tokens = tuple(component(value) for value in TOKEN.findall(base))
    suffix_key = tuple((SUFFIX.get(value.rstrip("0123456789"), 0),
                        int(value.lstrip("abcdefghijklmnopqrstuvwxyz") or "0"))
                       for value in suffixes)
    return tokens, suffix_key + ((EQUAL, EQUAL),), int(revision)


def matches(actual, operator, expected):
    """Проверить ограничение для кандидата на ребро."""
    if not operator:
        return True
    if not actual:
        return False
    if "~" in operator:
        return actual.startswith(expected)
    if operator == "=":
        return actual == expected
    left, right = version_key(actual), version_key(expected)
    return (("<" in operator and left < right)
            or (">" in operator and left > right)
            or ("=" in operator and left == right))
