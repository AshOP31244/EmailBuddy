/* Email Buddy — Service Worker */
const CACHE = 'emailbuddy-v1';
const OFFLINE_URL = '/offline/';

const PRECACHE = [
  '/',
  '/templates/',
  '/customers/',
  '/email/send/',
  '/email/logs/',
  '/reminders/',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap',
];

/* ── Install ─────────────────────────────────── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(PRECACHE.map(url => new Request(url, {cache: 'reload'}))))
      .catch(() => {}) // don't fail install if network is unavailable
  );
  self.skipWaiting();
});

/* ── Activate ────────────────────────────────── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

/* ── Fetch ───────────────────────────────────── */
self.addEventListener('fetch', event => {
  // Skip non-GET and Django admin / API calls
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/admin/')) return;
  if (event.request.url.includes('/api/')) return;
  if (event.request.url.includes('/accounts/')) return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      const networkFetch = fetch(event.request).then(response => {
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE).then(c => c.put(event.request, clone));
        }
        return response;
      });
      // Stale-while-revalidate
      return cached || networkFetch;
    }).catch(() => {
      // Offline fallback for HTML navigation
      if (event.request.mode === 'navigate') {
        return caches.match('/') || new Response(
          '<h1>Email Buddy — Offline</h1><p>Please reconnect to use the app.</p>',
          {headers: {'Content-Type': 'text/html'}}
        );
      }
    })
  );
});