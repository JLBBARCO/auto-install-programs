#!/usr/bin/env python3
import os
import shutil
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

if not SITE.exists():
    print('site/ folder not found; nothing to do.')
    exit(0)

moved = []
conflicts = []

def is_binary(path: Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
    except Exception:
        return True
    return False

for src_path in SITE.rglob('*'):
    if src_path.is_dir():
        continue
    rel = src_path.relative_to(SITE)
    dest = ROOT / rel
    dest_parent = dest.parent
    if not dest_parent.exists():
        dest_parent.mkdir(parents=True, exist_ok=True)

    if not dest.exists():
        # move file
        shutil.move(str(src_path), str(dest))
        moved.append(str(rel))
        continue

    # conflict: file exists at destination
    conflicts.append(str(rel))
    # special-case package.json: merge scripts and dependencies
    if rel.name == 'package.json':
        try:
            with open(dest, 'r', encoding='utf-8') as f:
                dest_json = json.load(f)
        except Exception:
            dest_json = {}
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                src_json = json.load(f)
        except Exception:
            src_json = {}

        merged = dest_json.copy()
        # merge top-level keys conservatively
        for key in ('scripts', 'dependencies', 'devDependencies', 'pnpm'):
            dest_k = dest_json.get(key, {}) if isinstance(dest_json.get(key, {}), dict) else {}
            src_k = src_json.get(key, {}) if isinstance(src_json.get(key, {}), dict) else {}
            merged_k = dest_k.copy()
            for k, v in src_k.items():
                if k not in merged_k:
                    merged_k[k] = v
            if merged_k:
                merged[key] = merged_k

        # for other keys not merged, keep existing dest value, else take from src
        for k, v in src_json.items():
            if k in ('scripts', 'dependencies', 'devDependencies', 'pnpm'):
                continue
            if k not in merged:
                merged[k] = v

        # backup dest
        shutil.copy2(str(dest), str(dest) + '.backup')
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        print(f'Merged package.json -> {dest} (backup created)')
        # remove source
        src_path.unlink()
        continue

    # for other conflicts: create a backup of dest, then append site content with a separator
    shutil.copy2(str(dest), str(dest) + '.backup-fromsite')
    try:
        if is_binary(src_path) or is_binary(dest):
            # if binary, keep both: save site file alongside with suffix
            alt = dest.with_name(dest.name + '.site')
            shutil.move(str(src_path), str(alt))
            print(f'Binary conflict: moved site file to {alt}')
        else:
            with open(dest, 'a', encoding='utf-8') as fdest, open(src_path, 'r', encoding='utf-8') as fsrc:
                fdest.write('\n\n/* --- APPENDED FROM site/{rel} --- */\n')
                fdest.write(fsrc.read())
            src_path.unlink()
            print(f'Appended site/{rel} into {dest} (backup created)')
    except Exception as e:
        print(f'Failed to merge {rel}: {e}')

# remove empty directories under site
for d in sorted([p for p in SITE.rglob('*') if p.is_dir()], key=lambda x: -len(str(x))):
    try:
        if not any(d.iterdir()):
            d.rmdir()
    except Exception:
        pass

# finally remove site root if empty
try:
    if not any(SITE.iterdir()):
        SITE.rmdir()
        print('site/ removed')
    else:
        print('site/ not empty after merge; leaving in place. Conflicts:', conflicts)
except Exception as e:
    print('Could not remove site/:', e)

print('Moved files:', len(moved))
print('Conflicts:', len(conflicts))
