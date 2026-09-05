"""Synchronize release metadata from version.py; --check makes no changes."""

import argparse
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / 'fusion_addin' / 'VersatzebenenTool'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = ast.parse((ADDIN / 'version.py').read_text(encoding='utf-8-sig'))
    version = next(ast.literal_eval(node.value) for node in source.body
                   if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in node.targets))
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('VERSION must use major.minor.patch format')

    patterns = {
        ADDIN / 'VersatzebenenTool.manifest': r'("version"\s*:\s*")[^"]+(")',
        ROOT / 'installer/VersatzebenenTool_installer.iss': r'(#define MyAppVersion ")[^"]+(")',
    }
    for filename in ('README.md', 'README.de.md', 'doku/version.md'):
        patterns[ROOT / filename] = r'(<!-- version:start -->\s*\*\*[^\n]*: )[\d.]+(\*\*\s*<!-- version:end -->)'
    json.loads((ADDIN / 'VersatzebenenTool.manifest').read_text(encoding='utf-8-sig'))
    updates = {}
    for path, pattern in patterns.items():
        content = path.read_text(encoding='utf-8-sig')
        updated, count = re.subn(pattern, lambda m: m[1] + version + m[2], content)
        if count != 1:
            raise ValueError(f'Expected one version declaration in {path}')
        if content != updated:
            updates[path] = updated
    for path, content in updates.items():
        print(('Out of date: ' if args.check else 'Updated: ') + str(path.relative_to(ROOT)))
        if not args.check:
            path.write_text(content, encoding='utf-8')
    if args.check and updates:
        return 1
    print(f'Version {version}: all current declarations are synchronized.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
