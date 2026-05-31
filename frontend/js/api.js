const originalFetch = window.fetch.bind(window);

window.fetch = (input, init = {}) => {
  const headers = new Headers(init.headers || {});
  if (window.location.hostname.includes("ngrok-free.app")) {
    headers.set("ngrok-skip-browser-warning", "true");
  }

  return originalFetch(input, {
    ...init,
    headers,
  });
};
