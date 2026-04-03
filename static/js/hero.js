/**
 * GFI — Hero
 *
 * Two behaviours:
 *  1. Set background-image on .hero__slide from data-bg attribute.
 *     (Avoids blocking <img> requests and keeps the HTML free of inline styles.)
 *  2. Stat counter animation — counts up from 0 to target with easeOut
 *     cubic, triggered once when the stats section scrolls into view.
 */

(() => {
    'use strict';

    /* ── 1. Hero slide backgrounds ─────────────────────────────────────────── */

    document.querySelectorAll('.hero__slide[data-bg]').forEach(el => {
        el.style.backgroundImage = `url(${el.dataset.bg})`;
    });

    /* ── 2. Stat counter animation ─────────────────────────────────────────── */

    const counters     = document.querySelectorAll('.stat-number');
    const statsSection = document.querySelector('.stats-section');

    if (!counters.length || !statsSection) return;

    const easeOutCubic = (t) => 1 - (1 - t) ** 3;

    const animateCounter = (el) => {
        const raw    = el.textContent.trim();
        const suffix = raw.replace(/[\d,]/g, '');
        const target = parseInt(raw.replace(/\D/g, ''), 10);

        /* Skip non-numeric stats (e.g. "SEA") */
        if (isNaN(target)) return;

        const duration = 1600;
        let start = null;

        const step = (timestamp) => {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            el.textContent = Math.round(easeOutCubic(progress) * target) + suffix;
            if (progress < 1) requestAnimationFrame(step);
        };

        requestAnimationFrame(step);
    };

    const counterObserver = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
            counters.forEach(animateCounter);
            counterObserver.disconnect();
        }
    }, { threshold: 0.3 });

    counterObserver.observe(statsSection);

})();
