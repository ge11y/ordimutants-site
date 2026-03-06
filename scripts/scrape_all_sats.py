#!/usr/bin/env python3
"""
Scrape sat names for all Ordi Mutants from ordinals.com
"""
import json, time, subprocess, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_sat_name(ins_id):
    """Get sat name for an inscription"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://ordinals.com/inscription/{ins_id}'],
            capture_output=True, text=True, timeout=15
        )
        
        # Extract sat name
        match = re.search(r'sat name.*?href=/sat/[^>]+>([^<]+)<', result.stdout)
        if match:
            return ins_id, match.group(1).strip()
        
        # Also try alternative pattern
        match2 = re.search(r'/sat/([a-z0-9]+)">([^<]+)</a>.*?sat name', result.stdout, re.IGNORECASE)
        if match2:
            return ins_id, match2.group(2).strip()
            
    except Exception as e:
        return ins_id, None
    return ins_id, None

# Rare sat keywords
RARE_SATS = {
    'vintage': 'Vintage',
    'silk road': 'Silk Road', 
    'silkroad': 'Silk Road',
    'hitman': 'Hitman',
    'pizza': 'Pizza',
    'jpeg': 'JPEG',
    'nakamoto': 'Nakamoto',
    'block 9': 'Block 9',
    'block 78': 'Block 78', 
    'block 286': 'Block 286',
    'block 666': 'Block 666',
    'first transaction': 'First Transaction',
    'alpha': 'Alpha',
    'omega': 'Omega',
    'palindrome': 'Palindrome',
    'black uncommon': 'Black Uncommon',
    'uncommon': 'Uncommon',
    'paliblock': 'Paliblock Palindrome',
    '450x': 'Block 9 450x',
}

def get_rare_sat(sat_name):
    """Check if sat name matches rare sat types"""
    if not sat_name:
        return None
    sat_lower = sat_name.lower()
    for keyword, rare_name in RARE_SATS.items():
        if keyword in sat_lower:
            return rare_name
    return None

# Load metadata
print("Loading metadata...")
data = json.load(open('/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/metadata.json'))
inscriptions = [m['id'] for m in data]

print(f"Processing {len(inscriptions)} inscriptions...")

# Process in batches with threading
results = {}
rare_count = 0
batch_size = 50

for i in range(0, len(inscriptions), batch_size):
    batch = inscriptions[i:i+batch_size]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_sat_name, ins_id): ins_id for ins_id in batch}
        
        for future in as_completed(futures):
            ins_id, sat_name = future.result()
            results[ins_id] = sat_name
            
            rare = get_rare_sat(sat_name)
            if rare:
                rare_count += 1
                print(f"  #{len(results)}: {ins_id[:20]}... -> {sat_name} = {rare}")
    
    # Progress every batch
    print(f"Progress: {i+len(batch)}/{len(inscriptions)} - Rare found: {rare_count}")
    
    # Small delay between batches
    time.sleep(1)

# Save results
print(f"\nSaving {len(results)} results...")
with open('/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/all_sats.json', 'w') as f:
    json.dump(results, f, indent=2)

# Also build mutant->rare sat mapping
mutant_to_rare = {}
for m in data:
    ins_id = m['id']
    name = m['meta']['name']
    match = re.search(r'#(\d+)', name)
    if match:
        mutant_num = int(match.group(1))
        if ins_id in results:
            rare = get_rare_sat(results[ins_id])
            if rare:
                mutant_to_rare[mutant_num] = rare

print(f"\nTotal rare sats found: {len(mutant_to_rare)}")
with open('/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/data/mutant_to_sat_full.json', 'w') as f:
    json.dump(mutant_to_rare, f, indent=2)

print("Done!")
