// Ordi Mutants Collection Viewer
// Combined CSV (rankings) + JSON (traits) + Ordinals.com images + Rare SAT badges

const rarityConfig = {
  'mythic': { color: '#fbbf24', icon: '💎', label: 'Mythic', sort: 1 },
  'legendary': { color: '#f59e0b', icon: '👑', label: 'Legendary', sort: 2 },
  'epic': { color: '#a855f7', icon: '⭐', label: 'Epic', sort: 3 },
  'rare': { color: '#3b82f6', icon: '💫', label: 'Rare', sort: 4 },
  'uncommon': { color: '#22c55e', icon: '✨', label: 'Uncommon', sort: 5 },
  'common': { color: '#6b7280', icon: '🔹', label: 'Common', sort: 6 }
};

const satBadgeConfig = {
  "Vintage": {"icon": "<img src='badges/badge_01.png' alt='Vintage'>", "color": "#fbbf24", "name": "Vintage"},
  "Silk Road": {"icon": "<img src='badges/badge_02.png' alt='Silk Road'>", "color": "#a0522d", "name": "Silk Road"},
  "Hitman": {"icon": "<img src='badges/badge_03.png' alt='Hitman'>", "color": "#dc143c", "name": "Hitman"},
  "Pizza": {"icon": "<img src='badges/badge_04.png' alt='Pizza'>", "color": "#ff6347", "name": "Pizza"},
  "JPEG": {"icon": "<img src='badges/badge_05.png' alt='JPEG'>", "color": "#ff69b4", "name": "JPEG"},
  "Block 666": {"icon": "<img src='badges/badge_06.png' alt='Block 666'>", "color": "#8b0000", "name": "Block 666"},
  "Nakamoto": {"icon": "<img src='badges/badge_07.png' alt='Nakamoto'>", "color": "#4a4a4a", "name": "Nakamoto"},
  "First Transaction": {"icon": "<img src='badges/badge_08.png' alt='First Transaction'>", "color": "#8b4513", "name": "First Transaction"},
  "Block 9": {"icon": "<img src='badges/badge_09.png' alt='Block 9'>", "color": "#ffffff", "name": "Block 9"},
  "Block 286": {"icon": "<img src='badges/badge_10.png' alt='Block 286'>", "color": "#ffd700", "name": "Block 286"},
  "Black Uncommon": {"icon": "<img src='badges/badge_11.png' alt='Black Uncommon'>", "color": "#000000", "name": "Black Uncommon"},
  "Palindrome": {"icon": "<img src='badges/badge_12.png' alt='Palindrome'>", "color": "#ff00ff", "name": "Palindrome"},
  "Omega": {"icon": "<img src='badges/badge_13.png' alt='Omega'>", "color": "#00ff00", "name": "Omega"},
  "Alpha": {"icon": "<img src='badges/badge_14.png' alt='Alpha'>", "color": "#00ffff", "name": "Alpha"},
  "Uncommon": {"icon": "<img src='badges/badge_15.png' alt='Uncommon'>", "color": "#228b22", "name": "Uncommon"},
  "Block 78": {"icon": "<img src='badges/badge_16.png' alt='Block 78'>", "color": "#9400d3", "name": "Block 78"},
  "Paliblock Palindrome": {"icon": "<img src='badges/badge_17.png' alt='Paliblock'>", "color": "#000000", "name": "Paliblock Palindrome"},
  "Block 9 450x": {"icon": "<img src='badges/badge_18.png' alt='Block 9 450x'>", "color": "#ff1493", "name": "Block 9 450x"},
  "Common": {"icon": "🔹", "color": "#6b7280", "name": "Common"}
};

let mutants = [];
let metadata = {};
let mutantToSat = {};
let mutantBadges = {}; // tokenId -> [badgeSlugs]
let currentSort = 'rank';
let currentFilter = 'all';

// Badge slug to config key mapping
const slugToKey = {
  'vintage': 'Vintage',
  'silk_road': 'Silk Road',
  'hitman': 'Hitman',
  'pizza': 'Pizza',
  'jpeg': 'JPEG',
  'nakamoto': 'Nakamoto',
  'block_9': 'Block 9',
  'block_286': 'Block 286',
  'black_uncommon': 'Black Uncommon',
  'first_transaction': 'First Transaction',
  'palindrome': 'Palindrome',
  'paliblock_palindrome': 'Paliblock Palindrome',
  'block_666': 'Block 666',
  'block_78': 'Block 78',
  'omega': 'Omega',
  'alpha': 'Alpha',
  'uncommon': 'Uncommon',
  'block_9_450x': 'Block 9 450x',
  'common': 'Common'
};

// Badge image mapping (slug -> badge filename)
const BADGE_IMAGE_MAP = {
  'vintage': 'badge_01.png',
  'silk_road': 'badge_02.png',
  'hitman': 'badge_03.png',
  'pizza': 'badge_04.png',
  'jpeg': 'badge_05.png',
  'block666': 'badge_06.png',
  'nakamoto': 'badge_07.png',
  'first_tx': 'badge_08.png',
  'block9': 'badge_09.png',
  'block286': 'badge_10.png',
  'black_uncommon': 'badge_11.png',
  'palindrome': 'badge_12.png',
  'omega': 'badge_13.png',
  'alpha': 'badge_14.png',
  'uncommon': 'badge_15.png',
  'block78': 'badge_16.png',
  'paliblock_palindrome': 'badge_17.png',
  'block9_450x': 'badge_18.png',
  'common': 'badge_01.png'
};

// Humanize slug for tooltip
function humanizeSlug(slug) {
  return slug.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function parseCSV(csv) {
  const lines = csv.trim().split('\n');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    return {
      rank: parseInt(values[0]),
      id: values[1],
      name: values[2],
      number: values[3] ? parseFloat(values[3]) : null,
      dna: values[4],
      rarityScore: parseFloat(values[5]),
      status: values[6]
    };
  });
}

function sortMutants(mutants, sortBy) {
  const sorted = [...mutants];
  switch(sortBy) {
    case 'rank': return sorted.sort((a, b) => a.rank - b.rank);
    case 'rarity': return sorted.sort((a, b) => {
      const rarityA = rarityConfig[a.status]?.sort || 999;
      const rarityB = rarityConfig[b.status]?.sort || 999;
      if (rarityA !== rarityB) return rarityA - rarityB;
      return b.rarityScore - a.rarityScore;
    });
    case 'number': return sorted.sort((a, b) => (a.number || 9999) - (b.number || 9999));
    case 'score': return sorted.sort((a, b) => b.rarityScore - a.rarityScore);
    default: return sorted;
  }
}

function filterMutants(mutants, filter) {
  if (filter === 'all') return mutants;
  return mutants.filter(m => m.status === filter);
}

function getTraits(id) {
  return metadata[id] || null;
}

function getImageUrl(id) {
  return `https://ordinals.com/content/${id}`;
}

function getRareSatBadge(mutantNumber) {
  // mutantNumber is the token ID (e.g., 0 for OG#0, 123 for #123)
  if (!mutantNumber) return '';
  
  const badges = mutantBadges[mutantNumber.toString()];
  if (!badges || badges.length === 0) return '';
  
  // Get rarest badge (first one, already sorted by rarity)
  const rarestSlug = badges[0];
  const badgeImg = BADGE_IMAGE_MAP[rarestSlug] || 'badge_01.png';
  const isBlack = rarestSlug === 'paliblock_palindrome';
  const style = isBlack ? 'filter: brightness(0) grayscale(100%);' : '';
  
  // Build all badges HTML for hover popup
  const allBadgesHtml = badges.map(slug => {
    const img = BADGE_IMAGE_MAP[slug] || 'badge_01.png';
    const black = slug === 'paliblock_palindrome';
    return `<div class="badge-popup-item" style="${black ? 'filter: brightness(0) grayscale(100%);' : ''}">
      <img src="badges/${img}" style="width:32px;height:32px;">
      <span>${humanizeSlug(slug)}</span>
    </div>`;
  }).join('');
  
  // If only 1 badge, just show it without popup
  if (badges.length === 1) {
    return `<img class="sat-badge-single" src="badges/${badgeImg}" title="${humanizeSlug(rarestSlug)}" style="${style}width:28px;height:28px;">`;
  }
  
  // Multiple badges - show stack with hover popup
  return `<div class="sat-badge-stack">
    <img class="sat-badge-main" src="badges/${badgeImg}" title="${humanizeSlug(rarestSlug)} (${badges.length} total)" style="${style}width:28px;height:28px;">
    <span class="sat-badge-count">+${badges.length - 1}</span>
    <div class="sat-badge-popup">
      <div class="badge-popup-title">All Badges</div>
      ${allBadgesHtml}
    </div>
  </div>`;
}

function renderCollection() {
  const grid = document.getElementById('collection-grid');
  let display = sortMutants(mutants, currentSort);
  display = filterMutants(display, currentFilter);
  
  const count = window.showAll ? display.length : 50;
  const shown = display.slice(0, count);
  
  grid.innerHTML = shown.map(m => {
    const cfg = rarityConfig[m.status] || rarityConfig.common;
    const traits = getTraits(m.id);
    const satNum = m.number ? Math.floor(m.number) : null;
    const imgUrl = getImageUrl(m.id);
    const satBadge = getRareSatBadge(satNum);
    
    let traitsHtml = '';
    if (traits && traits.meta && traits.meta.attributes) {
      traitsHtml = traits.meta.attributes.slice(0, 4).map(t => 
        `<div class="trait"><span class="trait-type">${t.trait_type}:</span> <span class="trait-value">${t.value}</span></div>`
      ).join('');
    }
    
    return `
      <div class="mutant-card" style="border-left: 3px solid ${cfg.color}">
        <div class="mutant-header">
          <span class="mutant-rank">#${m.rank}</span>
        </div>
        <div class="mutant-image">
          <img src="${imgUrl}" alt="${m.name}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23111%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2255%22 text-anchor=%22middle%22 fill=%22${cfg.color.replace('#','')}%22 font-size=%2240%22>${cfg.icon}</text></svg>'" />
          <div class="mutant-badges-bottom">${satBadge}</div>
        </div>
        <div class="mutant-name">${m.name || 'OrdiMutant'}</div>
        <div class="mutant-inscription">${m.id.substring(0, 22)}...</div>
        <div class="mutant-score">Score: ${m.rarityScore?.toFixed(1) || 'N/A'}</div>
        <div class="mutant-traits">${traitsHtml}</div>
        <div class="rarity-badge" style="color: ${cfg.color}">${cfg.label}</div>
        <a href="https://ordinals.com/inscription/${m.id}" target="_blank" class="view-ordinals">View on Ordinals ↗</a>
      </div>
    `;
  }).join('');
  
  document.getElementById('collection-count').textContent = 
    `${Math.min(count, display.length)} / ${display.length} mutants`;
}

function setSort(sort) {
  currentSort = sort;
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.sort === sort);
  });
  renderCollection();
}

function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === filter);
  });
  renderCollection();
}

function toggleShowAll() {
  window.showAll = !window.showAll;
  document.getElementById('show-all-btn').textContent = window.showAll ? 'Show Top 50' : 'Show All';
  renderCollection();
}

// Initialize
console.log("Loading collection data...");
Promise.all([
  fetch('data/mutants.csv').then(r => r.text()),
  fetch('data/metadata.json').then(r => r.json()),
  fetch('data/mutant_to_sat.json').then(r => r.json()),
  fetch('data/mutant_badges.json').then(r => r.json()).catch(() => ({}))
]).then(([csv, meta, satMap, badges]) => {
  console.log("Data loaded, processing...");
  mutants = parseCSV(csv);
  meta.forEach(m => { metadata[m.id] = m; });
  mutantToSat = satMap;
  mutantBadges = badges;
  renderCollection();
  
  // Stats
  const counts = {};
  mutants.forEach(m => { counts[m.status] = (counts[m.status] || 0) + 1; });
  
  let statsHtml = '';
  ['mythic', 'legendary', 'epic', 'rare', 'uncommon', 'common'].forEach(r => {
    if (counts[r]) {
      const cfg = rarityConfig[r];
      statsHtml += `<button class="filter-btn ${r === 'all' ? 'active' : ''}" data-filter="${r}" onclick="setFilter('${r}')" style="border-color: ${cfg.color}; color: ${cfg.color}">${cfg.icon} ${counts[r]}</button>`;
    }
  });
  statsHtml += `<button class="filter-btn all" data-filter="all" onclick="setFilter('all')" style="border-color: var(--text-dim)">All</button>`;
  document.getElementById('rarity-stats').innerHTML = statsHtml;
}).catch(err => {
  console.error("Error loading collection data:", err);
  document.getElementById('collection-grid').innerHTML = '<p style="color:red;">Error loading data. Check console for details.</p>';
});
