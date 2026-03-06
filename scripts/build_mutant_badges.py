#!/usr/bin/env python3
"""Build mutant badges mapping - maps ALL 2226 mutants, keeps duplicates"""

import json
import csv
import os

def slugify(name):
    if not name:
        return None
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[\s\-]+', '_', slug)
    slug = re.sub(r'[^a-z0-9_]', '', slug)
    slug = re.sub(r'_+', '_', slug)
    return slug.strip('_')

# Load satributes by inscription ID
DATA_DIR = '/Users/goobbotv3/.openclaw/workspace/ordimutants/data'
with open(os.path.join(DATA_DIR, 'satributes.json')) as f:
    satributes = {s['id']: slugify(s['satribute']) for s in json.load(f)}

print(f"Loaded {len(satributes)} satributes")

# Build mapping: collect ALL badges for each number
# Use both collection number AND inscription ID as keys
mapping = {}
RARITY = ['block_9_450x', 'alpha', 'omega', 'paliblock_palindrome', 'palindrome',
          'block_666', 'block_286', 'block_78', 'block_9', 'first_transaction',
          'nakamoto', 'pizza', 'hitman', 'silk_road', 'jpeg', 'vintage',
          'black_uncommon', 'uncommon', 'common']

with open(os.path.join(DATA_DIR, 'mutants.csv')) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ins_id = row['id']
        num = row.get('number', '').strip()
        
        if ins_id not in satributes:
            continue
        
        sat = satributes[ins_id]
        
        # Add by collection number
        if num:
            try:
                key = str(int(float(num)))
                if key not in mapping:
                    mapping[key] = set()
                mapping[key].add(sat)
            except:
                pass
        
        # Also add by inscription ID for special 1/1s
        if ins_id not in mapping:
            mapping[ins_id] = set()
        mapping[ins_id].add(sat)

# Convert sets to sorted lists
for k in mapping:
    mapping[k] = sorted(list(mapping[k]), key=lambda x: RARITY.index(x) if x in RARITY else 999)

print(f"Mapped {len(mapping)} entries")
print(f"With badges: {sum(1 for v in mapping.values() if v)}")

# Save
out_file = os.path.join(DATA_DIR, 'mutant_badges.json')
with open(out_file, 'w') as f:
    json.dump(mapping, f, indent=2)
print(f"Saved to {out_file}")

# Stats
from collections import Counter
counts = Counter()
for v in mapping.values():
    for b in v:
        counts[b] += 1
print("\nBadge distribution:")
for b, c in counts.most_common():
    print(f"  {b}: {c}")

# Check specific ones
print("\nChecking special mutants:")
for key in ['277950309d9120caed705724f0fae776ece50c91118af0e5ea0d8149528c48cdi0', 'f926209aa58f4f03b01d9691e6c29d05f77b6b87132f74cd6c2d2182f9726e4di0']:
    if key in mapping:
        print(f"  {key[:20]}...: {mapping[key]}")
