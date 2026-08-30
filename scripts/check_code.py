import sys


def check_file(path: str) -> bool:
    """Возвращает True, если файл в порядке, False — если найдено нарушение."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    consecutive_count = 0
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            consecutive_count += 1
            if consecutive_count > 2:
                print(f"{path}:{line_number}: more than 2 consecutive commented lines")
                return False
        else:
            consecutive_count = 0

    return True


if __name__ == "__main__":
    ok = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            ok = False
    sys.exit(0 if ok else 1)
