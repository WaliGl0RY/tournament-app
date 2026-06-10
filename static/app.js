// ── Core API helper ─────────────────────────────────────────────────
// All pages use this to call the Flask REST API.
// GET:  api('/api/me')
// POST: api('/api/login', 'POST', { username, pin })

async function api(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin'
  };
  if (body) opts.body = JSON.stringify(body);

  try {
    const res  = await fetch(url, opts);
    const data = await res.json();
    return data;
  } catch (e) {
    return { error: 'Network error' };
  }
}

// ── Logout ───────────────────────────────────────────────────────────
async function logout() {
  await api('/api/logout', 'POST');
  localStorage.clear();
  window.location.href = '/';
}

// ── Navbar bootstrap (runs on every page except login) ───────────────
(async () => {
  // Skip on the login/auth page
  if (!document.querySelector('.navbar')) return;

  const me = await api('/api/me');
  if (!me.logged_in) {
    window.location.href = '/';
    return;
  }

  // Fill in username
  const usernameEl = document.getElementById('nav-username');
  if (usernameEl) usernameEl.textContent = me.username;

  // Fill in tournament name
  const tname = localStorage.getItem('tournament_name');
  const nameEl = document.getElementById('nav-tournament-name');
  if (nameEl && tname) nameEl.textContent = tname;

  // Store admin status for use in pages
  localStorage.setItem('is_admin', me.is_admin || 0);
})();

// ── UI helpers ───────────────────────────────────────────────────────

// Generate a consistent background color from a string (for avatars)
function avatarColor(name) {
  const colors = [
    '#4a3728','#1a3a4a','#2a3a1a','#3a1a3a','#3a2a1a',
    '#1a2a3a','#3a1a1a','#1a3a2a','#2a1a3a','#3a3a1a'
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}

// Get initials from a name (e.g. "walid" → "WA")
function initials(name) {
  return name.slice(0, 2).toUpperCase();
}
