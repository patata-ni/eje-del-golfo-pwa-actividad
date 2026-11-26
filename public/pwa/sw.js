const VERSION = 'v1';
const PREFIX = 'eje-bitacora-actividad-';
const STATIC = PREFIX + 'shell-' + VERSION;
const DYNAMIC = PREFIX + 'datos-' + VERSION;
const ROOT = new URL('./', self.location.href);
const SHELL = ['./', './index.html', './app.css', './app.js', './db.js', './manifest.json', './icons/icon-192.png', './icons/icon-512.png', './icons/maskable-512.png'];
const absolute = path => new URL(path, ROOT).href;
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(STATIC);
    await cache.addAll(SHELL.map(absolute));
    // Seed only the public academic catalog so it is available on the first offline launch.
    const data = await caches.open(DYNAMIC);
    await data.add(absolute('./catalogo.json'));
    // Updates wait until old tabs close; never interrupt an unsaved incident.
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    await Promise.all((await caches.keys()).filter(key => key.startsWith(PREFIX) && ![STATIC, DYNAMIC].includes(key)).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== ROOT.origin || !url.pathname.startsWith(ROOT.pathname)) return;
  if (url.href === absolute('./catalogo.json')) {
    // Stale-while-revalidate for a bounded dynamic resource; failures keep the old catalog.
    const update = caches.open(DYNAMIC).then(async cache => {
      const response = await fetch(event.request);
      if (response.ok && (response.headers.get('content-type') || '').includes('application/json')) {
        const parsed = await response.clone().json();
        if (Array.isArray(parsed.rutas) && Array.isArray(parsed.unidades)) await cache.put(event.request, response.clone());
      }
      return response;
    });
    event.waitUntil(update.catch(() => undefined));
    event.respondWith(caches.open(DYNAMIC).then(async cache => (await cache.match(event.request)) || await update));
    return;
  }
  if (event.request.mode === 'navigate') {
    // Only the CSR app shell is cached; Laravel sessions and private pages stay outside this scope.
    event.respondWith(caches.open(STATIC).then(async cache => (await cache.match(absolute('./index.html'))) || fetch(event.request)));
    return;
  }
  if (SHELL.map(absolute).includes(url.href)) {
    event.respondWith(caches.open(STATIC).then(async cache => (await cache.match(event.request)) || fetch(event.request)));
  }
});
