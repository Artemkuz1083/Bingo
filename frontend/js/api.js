const originalFetch = window.fetch.bind(window);

window.fetch = (input, init = {}) => {
  const headers = new Headers(init.headers || {});
  headers.set("ngrok-skip-browser-warning", "true");

  return originalFetch(input, {
    ...init,
    headers,
  });
};
