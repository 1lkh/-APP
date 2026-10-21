const CACHE = "dong-dui-v14";
const SHELL = ["./", "./index.html", "./styles.css", "./app.js", "./动作增强数据.json", "./精选100动作.csv", "./训练计划.json", "./manifest.webmanifest", "./icon.svg", "./icon-192.png"];

self.addEventListener("install", event => event.waitUntil(
  caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())
));

self.addEventListener("activate", event => event.waitUntil(
  caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())
));

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  // 动图交给浏览器 HTTP 缓存（30 天），不占 Cache Storage
  if (url.pathname.startsWith("/videos/")) return;

  // 页面导航：始终先走网络，只有离线才用缓存，避免"刷新了还是旧版本"
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() => caches.match("./index.html").then(r => r || caches.match("./")))
    );
    return;
  }

  // 静态资源：先给缓存保证速度，同时后台更新（stale-while-revalidate）
  event.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req).then(res => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
