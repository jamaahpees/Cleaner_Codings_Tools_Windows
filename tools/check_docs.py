"""Check repository-relative Markdown links and image references without network access."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    documents = [ROOT / name for name in
                 ('README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md')]
    documents += sorted((ROOT / 'docs').glob('*.md'))
    failures = []
    checked = 0
    for document in documents:
        if not document.is_file():
            failures.append(f'{document.relative_to(ROOT)}: missing document')
            continue
        content = document.read_text(encoding='utf-8')
        content = re.sub(r'```.*?```', '', content, flags=re.S)
        for match in re.finditer(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', content):
            reference = match.group(1).strip('<>')
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            checked += 1
            path = unquote(parsed.path)
            target = ROOT / path.lstrip('/') if path.startswith('/') else document.parent / path
            if not target.exists():
                line = content[:match.start()].count('\n') + 1
                failures.append(f'{document.relative_to(ROOT)}:{line}: missing {reference}')
    for failure in failures:
        print(failure)
    print(f'Checked {len(documents)} documents and {checked} local links; {len(failures)} failures.')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
