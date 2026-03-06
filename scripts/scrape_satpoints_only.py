#!/usr/bin/env python3
"""
Minimal satpoint scraper for OrdiMutants.
Only queries satpoint API - uses local files for everything else.
"""

import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path

# Constants
DEFAULT_SLEEP = 2.5
DEFAULT_BATCH_SIZE = 200
CHECKPOINT_INTERVAL = 25

def load_inscriptions(path):
    """Load inscription IDs from text file (one per line)."""
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_metadata(path):
    """Load metadata JSON and create tokenId -> inscription_id mapping."""
    with open(path, 'r') as f:
        mutants = json.load(f)
    
    # Build mapping: tokenId -> inscription_id
    # tokenId is the number after # in the name (e.g., "ORDIMUTANT OG#0" -> 0)
    mapping = {}
    for mutant in mutants:
        inscription_id = mutant['id']
        name = mutant['meta']['name']
        # Extract number from name like "ORDIMUTANT OG#0" or "ORDIMUTANT #123"
        if '#' in name:
            token_id = int(name.split('#')[1].split()[0])
            mapping[token_id] = inscription_id
    
    return mapping

def load_checkpoint(outdir):
    """Load checkpoint if exists."""
    checkpoint_file = os.path.join(outdir, 'satpoints_checkpoint.json')
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {}

def save_checkpoint(outdir, data):
    """Save checkpoint."""
    checkpoint_file = os.path.join(outdir, 'satpoints_checkpoint.json')
    with open(checkpoint_file, 'w') as f:
        json.dump(data, f)

def query_satpoint(api_base, inscription_id, session, retries=3):
    """Query satpoint for a single inscription."""
    # Try both endpoint patterns: /inscription/{id}/satpoint and /api/inscription/{id}
    urls = [
        f"{api_base}/inscription/{inscription_id}/satpoint",
        f"{api_base}/inscription/{inscription_id}",
        f"{api_base}/api/inscription/{inscription_id}",
    ]
    
    for attempt in range(retries):
        for url in urls:
            try:
                resp = session.get(url, timeout=30)
                
                if resp.status_code == 200:
                    data = resp.json()
                    # Try to extract satpoint/sat from various response formats
                    satpoint = data.get('satpoint') or data.get('sat_point')
                    sat = data.get('sat') or data.get('number')
                    return {
                        'satpoint': satpoint,
                        'sat': sat
                    }
                elif resp.status_code == 404:
                    continue  # Try next URL
                elif resp.status_code == 429:
                    # Rate limited
                    retry_after = resp.headers.get('Retry-After', str(DEFAULT_SLEEP * 2))
                    wait_time = int(retry_after) if retry_after.isdigit() else DEFAULT_SLEEP * 2
                    print(f"  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  Error {resp.status_code} on {url}: {resp.text[:50]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  Request error on {url}: {e}")
                continue
            except json.JSONDecodeError:
                print(f"  Non-JSON response on {url}")
                continue
        
        # If we got here, all URLs failed
        time.sleep(2)
    
    return {'satpoint': None, 'sat': None, 'error': 'failed'}

def scrape(args):
    """Main scraping function."""
    print(f"=== Satpoint Scraper ===")
    print(f"Inscriptions file: {args.inscriptions}")
    print(f"Metadata file: {args.metadata}")
    print(f"Output dir: {args.outdir}")
    print(f"API base: {args.api_base}")
    print(f"Sleep: {args.sleep}s")
    
    # Load inputs
    inscriptions = load_inscriptions(args.inscriptions)
    token_mapping = load_metadata(args.metadata)
    
    print(f"Loaded {len(inscriptions)} inscriptions")
    print(f"Loaded {len(token_mapping)} token mappings")
    
    # Load checkpoint if resuming
    checkpoint = load_checkpoint(args.outdir)
    inscription_results = checkpoint.get('inscription_satpoints', {})
    missing = checkpoint.get('missing', [])
    
    # Track progress
    total = len(inscriptions)
    done = len(inscription_results)
    print(f"Already done: {done}/{total}")
    
    # Setup session
    session = requests.Session()
    
    # Process inscriptions
    start_time = time.time()
    for i, inscription_id in enumerate(inscriptions):
        # Skip if already done
        if inscription_id in inscription_results:
            continue
        
        # Query satpoint
        result = query_satpoint(args.api_base, inscription_id, session)
        inscription_results[inscription_id] = result
        
        if result.get('error'):
            missing.append(inscription_id)
        
        # Progress output
        done = i + 1
        if done % 10 == 0:
            elapsed = time.time() - start_time
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print(f"Progress: {done}/{total} ({done/total*100:.1f}%) - ETA: {eta/60:.1f}min")
        
        # Checkpoint
        if done % CHECKPOINT_INTERVAL == 0:
            save_checkpoint(args.outdir, {
                'inscription_satpoints': inscription_results,
                'missing': missing
            })
        
        # Rate limit
        if i < total - 1:
            time.sleep(args.sleep)
    
    # Final save
    print("\n=== Saving results ===")
    
    # Save inscription_satpoints.json
    inscription_output = os.path.join(args.outdir, 'inscription_satpoints.json')
    with open(inscription_output, 'w') as f:
        json.dump(inscription_results, f, indent=2)
    print(f"Saved: {inscription_output}")
    
    # Build and save mutant_satpoints.json
    mutant_results = {}
    for token_id, inscription_id in token_mapping.items():
        if inscription_id in inscription_results:
            sat_data = inscription_results[inscription_id]
            mutant_results[token_id] = {
                'inscription_id': inscription_id,
                'satpoint': sat_data.get('satpoint'),
                'sat': sat_data.get('sat')
            }
        else:
            mutant_results[token_id] = {
                'inscription_id': inscription_id,
                'satpoint': None,
                'sat': None
            }
    
    mutant_output = os.path.join(args.outdir, 'mutant_satpoints.json')
    with open(mutant_output, 'w') as f:
        json.dump(mutant_results, f, indent=2)
    print(f"Saved: {mutant_output}")
    
    # Save missing
    missing_output = os.path.join(args.outdir, 'missing_satpoints.txt')
    with open(missing_output, 'w') as f:
        for mid in missing:
            f.write(mid + '\n')
    print(f"Saved: {missing_output}")
    
    # Summary
    successful = sum(1 for r in inscription_results.values() if r.get('satpoint'))
    with_sat = sum(1 for r in inscription_results.values() if r.get('sat'))
    
    print(f"\n=== Summary ===")
    print(f"Total inscriptions: {total}")
    print(f"Successful satpoints: {successful}")
    print(f"With sat number: {with_sat}")
    print(f"Failed: {len(missing)}")
    
    # Cleanup checkpoint
    checkpoint_file = os.path.join(args.outdir, 'satpoints_checkpoint.json')
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

def main():
    parser = argparse.ArgumentParser(description='Scrape satpoints for inscriptions')
    parser.add_argument('--inscriptions', required=True, help='Path to inscriptions.txt')
    parser.add_argument('--metadata', required=True, help='Path to mutants metadata JSON')
    parser.add_argument('--outdir', default='data', help='Output directory')
    parser.add_argument('--api-base', default=os.environ.get('ORD_API_BASE') or os.environ.get('SATPOINT_API_BASE') or 'http://127.0.0.1:80', help='API base URL')
    parser.add_argument('--sleep', type=float, default=DEFAULT_SLEEP, help='Sleep between requests (seconds)')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE, help='Batch size (unused, for compatibility)')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    
    args = parser.parse_args()
    
    # Create outdir if needed
    os.makedirs(args.outdir, exist_ok=True)
    
    scrape(args)

if __name__ == '__main__':
    main()
