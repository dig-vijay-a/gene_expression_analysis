import { precacheAndRoute } from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import { StaleWhileRevalidate } from "workbox-strategies";

precacheAndRoute(self.__WB_MANIFEST || []);

// Cache API requests
registerRoute(
  ({ url }) => url.origin === "https://your-api.onrender.com",
  new StaleWhileRevalidate()
);

// Activate new service worker immediately
self.addEventListener("install", (event) => {
  self.skipWaiting();
});

// Take control of the page immediately
self.addEventListener("activate", (event) => {
  clients.claim();
});
