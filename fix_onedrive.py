from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
# Match Users/<username>/OneDrive/ with either slash style, preserving the final separator.
PATTERN = re.compile(rb'(?i)(Users[\\/][^\\/]+[\\/])OneDrive([\\/])')
EXTENSIONS = {'.html', '.htm', '.url', '.lnk'}


def main():
    changed = 0
    for path in sorted(BASE.iterdir()):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            original = path.read_bytes()
            updated, count = PATTERN.subn(rb'\1', original)
            # For UTF-16 LE shortcuts, bytes are interleaved with NULs.
            if path.suffix.lower() == '.lnk':
                for encoding in ('utf-16-le', 'utf-16-be'):
                    needle = re.compile(r'(?i)(Users[\\/][^\\/]+[\\/])OneDrive([\\/])')
                    try:
                        decoded = updated.decode(encoding)
                    except UnicodeError:
                        continue
                    fixed, n = needle.subn(r'\1', decoded)
                    if n:
                        updated = fixed.encode(encoding)
                        count += n
                        break
            if count and updated != original:
                path.write_bytes(updated)
                changed += 1
                print(f'[UPDATED] {path.name} ({count} replacements)')
            else:
                print(f'[SKIP] {path.name}')
        except Exception as exc:
            print(f'[ERROR] {path.name}: {exc}', file=sys.stderr)
    print(f'Finished. Updated {changed} file(s).')

if __name__ == '__main__':
    main()
