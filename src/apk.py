"""Чтение APKINDEX без менеджера пакетов."""

from dataclasses import dataclass
import io
import tarfile
from urllib.request import urlopen

TIMEOUT = 20
INDEX = "APKINDEX.tar.gz"
MAX_ARCHIVE = 32 * 1024 * 1024
MAX_INDEX = 128 * 1024 * 1024


@dataclass(frozen=True)
class Package:
    """Запись Alpine: имя, версия, требования и виртуальные имена."""

    name: str
    version: str
    dependencies: tuple[str, ...]
    provides: tuple[str, ...]


def parse_index(text):
    """Разобрать записи с полями P, V, D и p."""
    packages = []
    for record in text.split("\n\n"):
        fields = dict(line.split(":", 1) for line in record.splitlines()
                      if ":" in line)
        if "P" in fields and "V" in fields:
            packages.append(Package(
                fields["P"], fields["V"], tuple(fields.get("D", "").split()),
                tuple(fields.get("p", "").split()),
            ))
    if not packages:
        raise ValueError("в APKINDEX отсутствуют записи пакетов")
    return packages


def index_url(source):
    """Принять каталог архитектуры или адрес архива напрямую."""
    if source.endswith("/" + INDEX):
        return source
    return f"{source.rstrip('/')}/{INDEX}"


def load_index(source):
    """Скачать архив и прочитать только текстовый файл APKINDEX."""
    with urlopen(index_url(source), timeout=TIMEOUT) as response:
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValueError("архив APKINDEX слишком большой")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        entry = archive.getmember("APKINDEX")
        if not entry.isfile() or entry.size > MAX_INDEX:
            raise ValueError("неподдерживаемый файл APKINDEX")
        with archive.extractfile(entry) as index:
            return parse_index(index.read().decode("utf-8"))


def exact_package(packages, name, version):
    """Найти конкретную версию корневого пакета."""
    for package in packages:
        if package.name == name and package.version == version:
            return package
    raise ValueError(f"пакет {name} версии {version} отсутствует")
