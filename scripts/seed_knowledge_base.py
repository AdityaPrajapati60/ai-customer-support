from pathlib import Path

from app import db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def parse(path: Path) -> list[tuple[str, str, str]]:
    """Split a section file into (section, title, content) rows."""
    entries = []
    title = None
    content_lines: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if title is not None:
                content = "\n".join(content_lines).strip()
                if not content:
                    raise ValueError(f"Empty entry in {path.name}: {title}")
                entries.append((path.stem, title, content))
            title = line[3:].strip()
            if not title:
                raise ValueError(f"Empty heading in {path.name}")
            content_lines = []
        elif title is not None:
            content_lines.append(line)

    if title is not None:
        content = "\n".join(content_lines).strip()
        if not content:
            raise ValueError(f"Empty entry in {path.name}: {title}")
        entries.append((path.stem, title, content))

    if not entries:
        raise ValueError(f"No level-two headings found in {path}")
    return entries


def main() -> None:
    paths = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown files found in {KNOWLEDGE_BASE_DIR}")

    with db.connect() as conn:
        for path in paths:
            entries = parse(path)
            for section, title, content in entries:
                conn.execute(
                    """
                    insert into knowledge_base (section, title, content)
                    values (%s, %s, %s)
                    on conflict (section, title) do update
                      set content = excluded.content, updated_at = now()
                    """,
                    (section, title, content),
                )
            print(f"{path.stem}: {len(entries)} entries")


if __name__ == "__main__":
    main()
