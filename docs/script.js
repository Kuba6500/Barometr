// Barometr — renderuje summary.json wygenerowany przez scripts/generate_summary.py

async function loadSummary() {
  const app = document.getElementById('app');
  try {
    const res = await fetch('summary.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('summary.json niedostępny');
    const data = await res.json();
    render(data);
  } catch (err) {
    app.innerHTML = `<p class="error">Nie udało się wczytać dzisiejszego briefingu. ` +
      `Upewnij się, że summary.json istnieje obok tej strony (patrz README).</p>`;
    console.error(err);
  }
}

// Mapuje sentyment (-1..1) na kolor akcentu: czerwień (obawy) -> szarość (neutralnie) -> zieleń (spokojnie)
function sentimentColor(score) {
  const clamped = Math.max(-1, Math.min(1, score));
  if (clamped < 0) {
    // czerwień -> szarość
    const t = clamped + 1; // 0..1
    return lerpColor([176, 64, 46], [91, 107, 128], t);
  } else {
    // szarość -> zieleń
    const t = clamped; // 0..1
    return lerpColor([91, 107, 128], [47, 122, 79], t);
  }
}

function lerpColor(a, b, t) {
  const c = a.map((v, i) => Math.round(v + (b[i] - v) * t));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

function dialSVG(score) {
  // Igła obraca się od -60deg (obawy) przez 0deg (neutralnie) do +60deg (spokojnie)
  const angle = Math.max(-1, Math.min(1, score)) * 60;
  return `
  <svg class="dial-svg" width="120" height="70" viewBox="0 0 120 70" xmlns="http://www.w3.org/2000/svg">
    <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="var(--line)" stroke-width="8" stroke-linecap="round"/>
    <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="var(--accent)" stroke-width="8"
          stroke-linecap="round" stroke-dasharray="157" stroke-dashoffset="0" opacity="0.35"/>
    <line class="dial-needle" x1="60" y1="60" x2="60" y2="18" stroke="var(--accent)" stroke-width="3"
          stroke-linecap="round" style="transform: rotate(${angle}deg)"/>
    <circle cx="60" cy="60" r="5" fill="var(--accent)"/>
  </svg>`;
}

function changeClass(pct) {
  if (pct > 0.05) return 'up';
  if (pct < -0.05) return 'down';
  return 'flat';
}

function formatChange(pct) {
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}

function render(data) {
  const accent = sentimentColor(data.sentiment_score ?? 0);
  document.documentElement.style.setProperty('--accent', accent);

  const commentBySymbol = {};
  (data.assets || []).forEach(a => { commentBySymbol[a.symbol] = a.comment; });

  const rows = (data.raw_assets || []).map(asset => {
    const cls = changeClass(asset.change_pct);
    const comment = commentBySymbol[asset.symbol] || '';
    return `
      <div class="asset-row">
        <span class="asset-name">${asset.name}</span>
        <span class="asset-change ${cls}">${formatChange(asset.change_pct)}</span>
        ${comment ? `<p class="asset-comment">${comment}</p>` : ''}
      </div>`;
  }).join('');

  document.getElementById('app').innerHTML = `
    <span class="date-stamp">${data.date}</span>

    <section class="dial-section">
      ${dialSVG(data.sentiment_score ?? 0)}
      <div class="dial-copy">
        <p class="sentiment-label">${data.sentiment_label || 'Neutralnie'}</p>
        <p class="headline">${data.headline || ''}</p>
      </div>
    </section>

    <p class="overview">${data.overview || ''}</p>

    <h2 class="assets-heading">Rynki dzisiaj</h2>
    <div class="asset-list">${rows}</div>
  `;

  if (data.disclaimer) {
    document.getElementById('disclaimer').textContent = data.disclaimer;
  }
}

loadSummary();
