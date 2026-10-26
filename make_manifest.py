"""Write hashes for every distributable archive file except the manifest itself."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
files = [p for p in ROOT.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt' and '__pycache__' not in p.parts and not any(part.startswith('.') for part in p.relative_to(ROOT).parts)]
lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix() for p in sorted(files)]
(ROOT / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Hashed {len(files)} files')
