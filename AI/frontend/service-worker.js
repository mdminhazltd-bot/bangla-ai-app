const CACHE_NAME = "bangla-ai-cache-v1";
const FILES_TO_CACHE = [
  "./index.html",
  "./style.css",
  "./script.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png"
];

// Install: cache the core files so the app can open even with a weak connection
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(FILES_TO_CACHE))
  );
  self.skipWaiting();
});

// Activate: clean up old caches if the app is updated later
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Fetch: serve cached files when offline, but always let API calls (/ask) go to the network
self.addEventListener("fetch", (event) => {
  const url = event.request.url;

  // Never cache the AI API calls — always fetch fresh
  if (url.includes("/ask") || url.includes("/login") || url.includes("/signup")) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});