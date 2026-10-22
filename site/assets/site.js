/* Sunghong Park · small, dependency-free progressive enhancements. */
'use strict';
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const root = document.documentElement;
  // Preserve the old Jekyll homepage's section bookmarks after the redesign.
  const legacyAnchors = {
    '#curriculum-vitae': 'cv.html',
    '#research-interests': 'research.html',
    '#experience--education': 'cv.html#experience',
    '#grant--funding': 'projects.html',
    '#ongoing-research': 'projects.html#ongoing',
    '#journal-publications': 'publications.html',
    '#patent-achievements': 'archive.html?topic=patents',
    '#conference-presentations': 'archive.html?topic=conferences',
    '#awards--honors': 'cv.html#awards'
  };
  if (/(?:\/|\/index\.html)$/.test(location.pathname) && legacyAnchors[location.hash]) {
    location.replace(legacyAnchors[location.hash]);
    return;
  }
  const theme = $('[data-theme-toggle]');
  function syncThemeButton() {
    if (!theme) return;
    const dark = root.dataset.theme === 'dark';
    theme.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    theme.setAttribute('title', dark ? 'Switch to light theme' : 'Switch to dark theme');
    theme.setAttribute('aria-pressed', String(dark));
  }
  syncThemeButton();
  theme?.addEventListener('click', () => {
    const value = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = value;
    try { localStorage.setItem('sp-theme', value); } catch (_) { /* Optional persistence. */ }
    syncThemeButton();
  });

  // A non-modal, keyboard-accessible mobile navigation disclosure.
  const menu = $('[data-menu-toggle]');
  const nav = $('#main-navigation');
  function closeMenu(returnFocus = false) {
    if (!menu || !nav) return;
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
    if (returnFocus) menu.focus();
  }
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav?.classList.toggle('is-open', open);
  });
  nav?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') closeMenu(true);
  });
  document.addEventListener('click', event => {
    if (nav && menu && !nav.contains(event.target) && !menu.contains(event.target)) closeMenu();
  });
  window.matchMedia('(min-width: 701px)').addEventListener('change', event => { if (event.matches) closeMenu(); });

  // Graph controls change a conceptual map, not an experimental result.
  const map = $('#research-map-svg');
  const caption = $('#map-description');
  const captions = {
    graph: 'Learning useful representations from connected observations.',
    biomedical: 'Bringing biological structure into multimodal learning.',
    adaptation: 'Sharing information across domains while preserving differences.'
  };
  $$('[data-map-mode]').forEach(button => button.addEventListener('click', () => {
    const mode = button.dataset.mapMode;
    if (!map || !captions[mode]) return;
    map.dataset.mode = mode;
    $$('[data-map-mode]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    if (caption) caption.textContent = captions[mode];
  }));

  let toastTimer;
  function announce(message) {
    const toast = $('#toast');
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 4000);
  }
  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) { /* Fall through for browsers without clipboard permission. */ }
    const field = document.createElement('textarea');
    field.value = text;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.left = '-9999px';
    const host = $('dialog[open]') || document.body;
    host.append(field);
    const previous = document.activeElement;
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { /* Use manual fallback. */ }
    field.remove();
    previous?.focus();
    return copied;
  }
  $$('[data-copy-email]').forEach(button => button.addEventListener('click', async () => {
    const success = await copyText(button.dataset.copyEmail);
    announce(success ? 'Email address copied.' : 'Copy the email address from the link above.');
  }));

  // Search and filters work on pre-rendered HTML, so no content depends on JS.
  const filters = $('[data-filter-root]');
  if (filters) {
    const items = $$('[data-filter-item]');
    const input = $('[data-search]', filters);
    const year = $('[data-year]', filters);
    const chips = $$('[data-filter]', filters);
    const count = $('[data-result-count]');
    const empty = $('[data-empty]');
    const reset = $('[data-reset]');
    let category = 'all';
    const query = new URLSearchParams(window.location.search);
    if (input) input.value = query.get('q') || '';
    if (year && [...year.options].some(option => option.value === query.get('year'))) year.value = query.get('year');
    if (chips.some(chip => chip.dataset.filter === query.get('topic'))) category = query.get('topic');
    const normalize = value => String(value || '').normalize('NFKC').toLocaleLowerCase().trim();
    const cache = new Map(items.map(item => [item, normalize(item.textContent)]));
    function applyFilters(updateUrl = true) {
      const terms = normalize(input?.value).split(/\s+/).filter(Boolean);
      const selectedYear = year?.value || 'all';
      let visible = 0;
      items.forEach(item => {
        const matches = terms.every(term => cache.get(item).includes(term)) &&
          (selectedYear === 'all' || item.dataset.year === selectedYear) &&
          (category === 'all' || (item.dataset.topics || '').split('|').includes(category));
        item.hidden = !matches;
        if (matches) visible += 1;
      });
      chips.forEach(chip => chip.setAttribute('aria-pressed', String(chip.dataset.filter === category)));
      if (count) count.textContent = `${visible} of ${items.length} ${filters.dataset.resultNoun || 'records'}`;
      if (empty) empty.hidden = visible !== 0;
      if (updateUrl) {
        const params = new URLSearchParams();
        if (input?.value.trim()) params.set('q', input.value.trim());
        if (selectedYear !== 'all') params.set('year', selectedYear);
        if (category !== 'all') params.set('topic', category);
        try { history.replaceState(null, '', `${location.pathname}${params.size ? '?' + params : ''}${location.hash}`); }
        catch (_) { /* file:// previews can restrict history updates. */ }
      }
    }
    input?.addEventListener('input', () => applyFilters());
    year?.addEventListener('change', () => applyFilters());
    chips.forEach(chip => chip.addEventListener('click', () => { category = chip.dataset.filter; applyFilters(); }));
    reset?.addEventListener('click', () => {
      if (input) input.value = '';
      if (year) year.value = 'all';
      category = 'all';
      applyFilters();
      input?.focus();
    });
    filters.addEventListener('submit', event => event.preventDefault());
    applyFilters(false);
  }

  // Plain-text and BibTeX citation dialog. Native dialog supplies focus trapping.
  const dialog = $('#citation-dialog');
  const citationData = window.SITE_DATA?.citations || {};
  const citationField = $('#citation-text');
  let currentCitation = null;
  let citationFormat = 'text';
  let trigger = null;
  function showCitationFormat(format) {
    if (!currentCitation || !citationField) return;
    citationFormat = format;
    citationField.value = currentCitation[format] || '';
    $$('[data-citation-format]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.citationFormat === format)));
  }
  $$('[data-cite]').forEach(button => button.addEventListener('click', () => {
    currentCitation = citationData[button.dataset.cite];
    if (!currentCitation || !dialog) return;
    trigger = button;
    $('#citation-paper-title').textContent = currentCitation.title;
    showCitationFormat('text');
    dialog.showModal();
  }));
  $$('[data-citation-format]').forEach(button => button.addEventListener('click', () => showCitationFormat(button.dataset.citationFormat)));
  $('[data-close-dialog]')?.addEventListener('click', () => dialog?.close());
  dialog?.addEventListener('close', () => trigger?.focus());
  dialog?.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  $('[data-copy-citation]')?.addEventListener('click', async () => {
    if (!citationField) return;
    const success = await copyText(citationField.value);
    if (!success) { citationField.focus(); citationField.select(); }
    const message = success ? `${citationFormat === 'bibtex' ? 'BibTeX' : 'Citation'} copied.` : 'Text selected. Press Ctrl+C or Command+C to copy.';
    $('#citation-feedback').textContent = message;
  });
  $$('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
})();
