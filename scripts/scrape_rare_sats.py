#!/usr/bin/env python3
"""
Ordi Mutants Rare SAT Scraper
Scrapes Magic Eden to build mutant# -> rare sat mapping
"""

import json, re, time, os

SAT_URLS = {
    "Vintage": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Vintage%22%2C%22label%22%3A%22Vintage%22%2C%22count%22%3A637%2C%22floor%22%3A%220.00200%22%2C%22image%22%3A%22%22%2C%22total%22%3A637%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Silk Road": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Silk+Road%22%2C%22label%22%3A%22Silk+Road%22%2C%22count%22%3A484%2C%22floor%22%3A%220.00139%22%2C%22image%22%3A%22%22%2C%22total%22%3A484%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Hitman": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Hitman%22%2C%22label%22%3A%22Hitman%22%2C%22count%22%3A415%2C%22floor%22%3A%220.00145%22%2C%22image%22%3A%22%22%2C%22total%22%3A415%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Pizza": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Pizza%22%2C%22label%22%3A%22Pizza%22%2C%22count%22%3A407%2C%22floor%22%3A%220.00139%22%2C%22image%22%3A%22%22%2C%22total%22%3A407%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "JPEG": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22JPEG%22%2C%22label%22%3A%22JPEG%22%2C%22count%22%3A258%2C%22floor%22%3A%220.00140%22%2C%22image%22%3A%22%22%2C%22total%22%3A258%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Block 666": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Block+666%22%2C%22label%22%3A%22Block+666%22%2C%22count%22%3A226%2C%22floor%22%3A%220.00200%22%2C%22image%22%3A%22%22%2C%22total%22%3A226%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Nakamoto": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Nakamoto%22%2C%22label%22%3A%22Nakamoto%22%2C%22count%22%3A224%2C%22floor%22%3A%220.00334%22%2C%22image%22%3A%22%22%2C%22total%22%3A224%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "First Transaction": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22First+Transaction%22%2C%22label%22%3A%22First+Transaction%22%2C%22count%22%3A133%2C%22floor%22%3A%220.00625%22%2C%22image%22%3A%22%22%2C%22total%22%3A133%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Block 9": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Block+9%22%2C%22label%22%3A%22Block+9%22%2C%22count%22%3A133%2C%22floor%22%3A%220.00625%22%2C%22image%22%3A%22%22%2C%22total%22%3A133%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Block 286": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Block+286%22%2C%22label%22%3A%22Block+286%22%2C%22count%22%3A91%2C%22floor%22%3A%220.00334%22%2C%22image%22%3A%22%22%2C%22total%22%3A91%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Black Uncommon": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Black+Uncommon%22%2C%22label%22%3A%22Black+Uncommon%22%2C%22count%22%3A16%2C%22floor%22%3A%220.56900%22%2C%22image%22%3A%22%22%2C%22total%22%3A16%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Palindrome": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Palindrome%22%2C%22label%22%3A%22Palindrome%22%2C%22count%22%3A9%2C%22floor%22%3A%220.25500%22%2C%22image%22%3A%22%22%2C%22total%22%3A9%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Omega": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Omega%22%2C%22label%22%3A%22Omega%22%2C%22count%22%3A9%2C%22floor%22%3A%220.12500%22%2C%22image%22%3A%22%22%2C%22total%22%3A9%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Alpha": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Alpha%22%2C%22label%22%3A%22Alpha%22%2C%22count%22%3A5%2C%22floor%22%3A%220.07200%22%2C%22image%22%3A%22%22%2C%22total%22%3A5%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Uncommon": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Uncommon%22%2C%22label%22%3A%22Uncommon%22%2C%22count%22%3A4%2C%22floor%22%3A%220.20000%22%2C%22image%22%3A%22%22%2C%22total%22%3A4%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Block 78": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Block+78%22%2C%22label%22%3A%22Block+78%22%2C%22count%22%3A4%2C%22floor%22%3A%220.05400%22%2C%22image%22%3A%22%22%2C%22total%22%3A4%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Paliblock Palindrome": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Paliblock+Palindrome%22%2C%22label%22%3A%22Paliblock+Palindrome%22%2C%22count%22%3A2%2C%22floor%22%3A%220.25500%22%2C%22image%22%3A%22%22%2C%22total%22%3A2%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
    "Block 9 450x": "https://magiceden.us/ordinals/marketplace/ordimutants?selectedAttributes=%7B%22satribute%22%3A%5B%7B%22traitType%22%3A%22satribute%22%2C%22value%22%3A%22Block+9+450x%22%2C%22label%22%3A%22Block+9+450x%22%2C%22count%22%3A1%2C%22floor%22%3A%22--%22%2C%22image%22%3A%22%22%2C%22total%22%3A1%2C%22listedPercentage%22%3A%22%22%7D%5D%7D",
}

# Rarity tier for sorting (lower = rarer)
RARITY_TIER = {
    "Block 9 450x": 1,
    "Paliblock Palindrome": 2,
    "Alpha": 3,
    "Omega": 4,
    "Palindrome": 5,
    "Block 78": 6,
    "Uncommon": 7,
    "Black Uncommon": 8,
    "Block 286": 9,
    "Block 9": 10,
    "First Transaction": 11,
    "Nakamoto": 12,
    "Block 666": 13,
    "JPEG": 14,
    "Pizza": 15,
    "Hitman": 16,
    "Silk Road": 17,
    "Vintage": 18,
}

def get_mutant_numbers_from_snapshot(snapshot_text):
    """Extract mutant numbers from Magic Eden page snapshot"""
    # Pattern: ORDIMUTANT #123 or ORDIMUTANT OG #456
    pattern = r'ORDIMUTANT(?: OG)? #(\d+)'
    matches = re.findall(pattern, snapshot_text)
    return [int(m) for m in matches]

def load_metadata():
    """Load metadata and build number -> inscription mapping"""
    data = json.load(open('/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/metadata.json'))
    num_to_id = {}
    for m in data:
        name = m['meta']['name']
        match = re.search(r'#(\d+)', name)
        if match:
            num = int(match.group(1))
            num_to_id[num] = m['id']
    return num_to_id

def save_progress(data, filename='rare_sats_progress.json'):
    with open(f'/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/{filename}', 'w') as f:
        json.dump(data, f, indent=2)

def load_progress(filename='rare_sats_progress.json'):
    path = f'/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/{filename}'
    if os.path.exists(path):
        return json.load(open(path))
    return {}

print("Ordi Mutants Rare SAT Scraper")
print("=" * 50)
print(f"Total sat types: {len(SAT_URLS)}")
print("This will run through all 18 rare sat types")
print("=" * 50)
