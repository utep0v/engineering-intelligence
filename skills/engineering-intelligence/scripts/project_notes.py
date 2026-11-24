"""Локальные Markdown-записи о проекте. На вход подают только очищенный текст."""

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def default_store():
    state = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    return Path(state) / "engineering-intelligence" / "projects"


def journal_for(project, store):
    root = project.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Укажи существующий каталог проекта.")
    project_id = hashlib.sha256(os.fsencode(root)).hexdigest()
    requested = store.expanduser()
    directory = requested.resolve() / project_id
    if directory.is_symlink():
        raise ValueError("Каталог журнала оказался символической ссылкой.")
    for path in (Path(os.path.abspath(requested)), directory):
        for parent in (path, *path.parents):
            try:
                if parent.samefile(root):
                    raise ValueError("Журнал должен находиться за пределами проекта.")
            except FileNotFoundError:
                continue
    return directory


def make_private_directory(path):
    missing = []
    for parent in (path, *path.parents):
        if parent.exists():
            break
        missing.append(parent)
    for parent in reversed(missing):
        parent.mkdir(mode=0o700, exist_ok=True)


def read_entry(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Вместо обычного файла записи обнаружена ссылка или специальный файл.")
    with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)), "rb") as handle:
        data = handle.read()
    if hashlib.sha256(data).hexdigest() == path.stem:
        # В прежнем формате весь файл был текстом записи без даты сохранения.
        return "", data.decode("utf-8")
    header, _, body = data.partition(b"\n")
    stamp = re.fullmatch(rb"<!-- engineering-intelligence saved (\S+) -->", header)
    if not stamp or hashlib.sha256(body).hexdigest() != path.stem:
        raise ValueError(f"Содержимое записи изменено вне журнала: {path.name}")
    saved = datetime.strptime(stamp[1].decode("ascii"), UTC_FORMAT).strftime(UTC_FORMAT)
    return saved, body.decode("utf-8")


def add(directory, note):
    if not note.strip():
        raise ValueError("Пустую запись сохранить нельзя.")
    data = (note.rstrip("\n") + "\n").encode("utf-8")
    target = directory / (hashlib.sha256(data).hexdigest() + ".md")
    make_private_directory(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Записи можно добавлять только в обычный каталог журнала.")
    descriptor, temporary = tempfile.mkstemp(dir=directory, prefix=".entry-")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            saved = datetime.now(timezone.utc).strftime(UTC_FORMAT)
            handle.write(f"<!-- engineering-intelligence saved {saved} -->\n".encode("ascii"))
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            # Жёсткая ссылка публикует целую запись без замены уже опубликованной.
            os.link(temporary, target)
        except FileExistsError:
            read_entry(target)
            print(f"Такая запись уже есть в {target}")
        else:
            print(f"Запись сохранена в {target}")
    finally:
        os.unlink(temporary)


def show(directory, query):
    records = []
    search = query.casefold() if query else ""
    if directory.exists():
        for path in directory.iterdir():
            if not re.fullmatch(r"[0-9a-f]{64}\.md", path.name):
                continue
            saved, text = read_entry(path)
            if search in path.stem or search in text.casefold():
                records.append((saved, path.stem, text))
    if records:
        for saved, identifier, text in sorted(records):
            when = f"Сохранено {saved}" if saved else "Дата создания неизвестна"
            print(f"## {when} · ID `{identifier}`\n\n{text}")
    else:
        print("Совпадений нет." if query else "Сохранённых записей нет.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("show", help="Прочитать записи о проекте")
    listing.add_argument("--find", metavar="TEXT", help="Поиск по ID и тексту без учёта регистра")
    writing = commands.add_parser("add", help="Сохранить одну Markdown-запись из stdin")
    for command in (listing, writing):
        command.add_argument("project_root", type=Path, metavar="PROJECT_ROOT")
        command.add_argument("--store", type=Path, default=default_store(), metavar="DIR")
    args = parser.parse_args()
    try:
        directory = journal_for(args.project_root, args.store)
        if args.command == "show":
            show(directory, args.find)
        else:
            add(directory, sys.stdin.read())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
