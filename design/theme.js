/* Runs before CSS to avoid flashing the wrong theme. Storage may be blocked. */
(() => {
  document.documentElement.classList.add('js');
  try {
    const saved = localStorage.getItem('sp-theme');
    if (saved === 'dark' || saved === 'light') document.documentElement.dataset.theme = saved;
  } catch (_) { /* Private/file browsing still works without persistence. */ }
})();
