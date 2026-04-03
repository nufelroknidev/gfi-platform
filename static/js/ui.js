/**
 * GFI — UI Utilities
 *
 * Small interactive behaviours that apply site-wide:
 *  - Back-to-top button smooth scroll.
 */

(() => {
    'use strict';

    /* ── Back-to-top ─────────────────────────────────────────────────────── */

    const btn = document.getElementById('backToTop');
    if (!btn) return;

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

})();
