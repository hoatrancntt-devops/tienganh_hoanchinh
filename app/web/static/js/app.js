/* Tiện ích dùng chung: theme, fetch JSON, thông báo, đăng xuất. */
(function () {
  const KEY = 'efw-theme';
  // Áp dụng chế độ: 'light' | 'dark' | 'auto' (theo hệ thống)
  window.applyTheme = function (mode) {
    if (!mode || mode === 'auto') {
      localStorage.removeItem(KEY);
      document.documentElement.dataset.theme =
        window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    } else {
      localStorage.setItem(KEY, mode);
      document.documentElement.dataset.theme = mode;
    }
  };
  window.currentThemeMode = function () { return localStorage.getItem(KEY) || 'auto'; };
  const saved = localStorage.getItem(KEY);
  document.documentElement.dataset.theme =
    saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  // Nút nhanh trên header: bấm để đảo sáng/tối.
  const tb = document.getElementById('themeBtn');
  if (tb) tb.onclick = () =>
    window.applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
})();

async function api(url, data, method) {
  const opt = { method: method || (data ? 'POST' : 'GET'), headers: {} };
  if (data) { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(data); }
  const r = await fetch(url, opt);
  let j = {};
  try { j = await r.json(); } catch (e) { /* 204 hoặc HTML */ }
  return { ok: r.ok, status: r.status, data: j };
}

function toast(text, kind) {
  const el = document.createElement('div');
  el.className = 'alert alert-' + (kind || 'info');
  el.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);bottom:5rem;z-index:99;max-width:90vw;box-shadow:var(--shadow)';
  el.textContent = text;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

async function logout() {
  await api('/api/v1/auth/logout', {});
  location.href = '/login';
}

function timeAgo(iso) {
  const s = (Date.now() - new Date(iso)) / 1000;
  if (s < 60) return 'vừa xong';
  if (s < 3600) return Math.floor(s / 60) + ' phút trước';
  if (s < 86400) return Math.floor(s / 3600) + ' giờ trước';
  if (s < 604800) return Math.floor(s / 86400) + ' ngày trước';
  return new Date(iso).toLocaleDateString('vi-VN');
}

(function () {
  const btn = document.getElementById('notifBtn');
  const panel = document.getElementById('notifPanel');
  if (!btn || !panel) return;
  btn.onclick = async (e) => {
    e.stopPropagation();
    if (!panel.hidden) { panel.hidden = true; btn.setAttribute('aria-expanded', 'false'); return; }
    panel.innerHTML = '<div class="empty"><span class="spin"></span></div>';
    panel.hidden = false;
    btn.setAttribute('aria-expanded', 'true');
    const r = await fetch('/partials/notifications');
    panel.innerHTML = await r.text();
  };
  document.addEventListener('click', (e) => {
    if (!panel.hidden && !panel.contains(e.target)) {
      panel.hidden = true; btn.setAttribute('aria-expanded', 'false');
    }
  });
  setInterval(async () => {
    const r = await api('/api/v1/notifications/unread-count');
    if (!r.ok) return;
    let b = document.getElementById('notifBadge');
    const n = r.data.unread;
    if (n > 0 && !b) { b = document.createElement('span'); b.className = 'badge'; b.id = 'notifBadge'; btn.appendChild(b); }
    if (b) { if (n > 0) b.textContent = n < 10 ? n : '9+'; else b.remove(); }
  }, 60000);
})();

async function markAllRead() {
  await api('/api/v1/notifications/read-all', {});
  location.reload();
}
