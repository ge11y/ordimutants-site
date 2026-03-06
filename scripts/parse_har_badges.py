#!/usr/bin/env python3
"""
Parse HAR files from SATRIBUTE JSON folders and extract badge data.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

# Badge name mapping (folder name -> lowercase slug)
BADGE_MAP = {
    'BLOCK666.226': 'block666',
    'BLOCK9.133': 'block9',
    'Blackuncommon16': 'black_uncommon',
    'FIRSTTX133': 'first_tx',
    'HITMAN 415': 'hitman',
    'JPEG258': 'jpeg',
    'NAKAMOTO224': 'nakamoto',
    'PIZZA407': 'pizza',
    'SILKROAD 484': 'silk_road',
    'VINTAGE 637': 'vintage',
    'alpha5': 'alpha',
    'block286.91': 'block286',
    'block78.4': 'block78',
    'block9450x.1': 'block9_450x',
    'omega9': 'omega',
    'palendrome9': 'palindrome',
    'paliblockpalendrome2': 'paliblock_palindrome',
    'uncommon4': 'uncommon',
}

def parse_har_folder(folder_path):
    """Parse a HAR folder and extract inscription IDs."""
    har_path = os.path.join(folder_path, 'magiceden.us.har')
    if not os.path.exists(har_path):
        print(f"  No HAR file in {folder_path}")
        return []
    
    try:
        with open(har_path, 'r') as f:
            har = json.load(f)
    except Exception as e:
        print(f"  Error parsing {har_path}: {e}")
        return []
    
    entries = har.get('log', {}).get('entries', [])
    inscription_ids = []
    
    for entry in entries:
        url = entry.get('request', {}).get('url', '')
        if 'v2/ord/btc/tokens' in url:
            try:
                content = entry.get('response', {}).get('content', {}).get('text', '')
                if content:
                    data = json.loads(content)
                    tokens = data.get('tokens', [])
                    for token in tokens:
                        ins_id = token.get('id')
                        if ins_id:
                            inscription_ids.append(ins_id)
            except Exception as e:
                pass
    
    return inscription_ids

def main():
    base_path = "/Users/goobbotv3/Desktop/SATRIBUTE JSON"
    
    # Track badge memberships
    # inscription_id -> set of badges
    badge_membership = defaultdict(set)
    
    # Track unmatched
    unmatched = []
    
    # Parse each folder
    folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    
    print(f"Found {len(folders)} folders to process\n")
    
    for folder in sorted(folders):
        folder_path = os.path.join(base_path, folder)
        badge_slug = BADGE_MAP.get(folder, folder.lower().replace(' ', '_').replace('.', '_'))
        
        print(f"Processing: {folder} -> {badge_slug}")
        
        inscription_ids = parse_har_folder(folder_path)
        print(f"  Found {len(inscription_ids)} inscriptions")
        
        for ins_id in inscription_ids:
            badge_membership[ins_id].add(badge_slug)
    
    # Build output data
    all_badges = []
    by_id = {}
    
    for ins_id, badges in sorted(badge_membership.items()):
        badges_list = sorted(list(badges))
        all_badges.append({
            'inscription_id': ins_id,
            'badges': badges_list
        })
        by_id[ins_id] = {
            'badges': badges_list
        }
    
    print(f"\n=== Summary ===")
    print(f"Total unique inscriptions: {len(badge_membership)}")
    
    # Count badges
    from collections import Counter
    badge_counts = Counter()
    for badges in badge_membership.values():
        for b in badges:
            badge_counts[b] += 1
    
    print(f"\nBadge counts:")
    for badge, count in badge_counts.most_common():
        print(f"  {badge}: {count}")
    
    # Save output files
    out_dir = "/Users/goobbotv3/.openclaw/workspace/ordimutants-site/data"
    os.makedirs(out_dir, exist_ok=True)
    
    # Load existing metadata to get names
    metadata_path = os.path.join(out_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            metadata = json.load(f)
        # Create name lookup
        name_lookup = {}
        for m in metadata:
            ins_id = m.get('id')
            name = m.get('meta', {}).get('name', '')
            if ins_id and name:
                name_lookup[ins_id] = name
        
        # Add names to output
        for item in all_badges:
            ins_id = item['inscription_id']
            item['name'] = name_lookup.get(ins_id, '')
        
        for ins_id in by_id:
            by_id[ins_id]['name'] = name_lookup.get(ins_id, '')
    
    # Save ordimutants_badges.json
    with open(os.path.join(out_dir, 'ordimutants_badges.json'), 'w') as f:
        json.dump(all_badges, f, indent=2)
    print(f"\nSaved: {os.path.join(out_dir, 'ordimutants_badges.json')}")
    
    # Save ordimutants_badges_by_id.json
    with open(os.path.join(out_dir, 'ordimutants_badges_by_id.json'), 'w') as f:
        json.dump(by_id, f, indent=2)
    print(f"Saved: {os.path.join(out_dir, 'ordimutants_badges_by_id.json')}")
    
    # Save unmatched (empty for now - all matched via inscription_id)
    with open(os.path.join(out_dir, 'unmatched_har_entries.json'), 'w') as f:
        json.dump({'unmatched': [], 'notes': 'All entries matched via inscription_id'}, f, indent=2)
    print(f"Saved: {os.path.join(out_dir, 'unmatched_har_entries.json')}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
