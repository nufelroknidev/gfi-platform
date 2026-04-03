/**
 * GFI — Navbar
 *
 * Two behaviours:
 *  1. Scroll observer — adds .navbar-gfi--past-hero when the hero/page-header
 *     is no longer visible, and animates the topbar height + logo size.
 *  2. Inline search — expand/collapse the search input between News and CTA.
 */

(() => {
    'use strict';

    const nav    = document.getElementById('gfiNav');
    const heroEl = document.querySelector('.hero, .page-header');

    /* ── 1. Scroll observer ────────────────────────────────────────────────── */

    if (heroEl) {
        const scrollObserver = new IntersectionObserver(([entry]) => {
            nav.classList.toggle('navbar-gfi--past-hero', !entry.isIntersecting);
        }, { threshold: 0 });

        scrollObserver.observe(heroEl);
    }

    /* ── Topbar logo-size animation on scroll ─────────────────────────────── */

    const topbar = document.querySelector('.topbar');
    const logo   = nav?.querySelector('.navbar-logo');
    const brand  = nav?.querySelector('.navbar-brand');

    if (topbar && logo && brand) {
        const tbNatural = topbar.getBoundingClientRect().height;
        const navTop    = nav.getBoundingClientRect().top;
        const brandTop  = brand.getBoundingClientRect().top;
        const maxShift  = Math.max(0, brandTop - navTop);
        const logoNatH  = logo.getBoundingClientRect().height;

        const applyLogoSize = (tbH) => {
            const ratio           = tbNatural > 0 ? tbH / tbNatural : 0;
            topbar.style.height   = `${tbH}px`;
            topbar.style.opacity  = ratio;
            logo.style.height     = `${logoNatH * (0.8 + 0.2 * ratio)}px`;
            brand.style.marginTop = `${-ratio * maxShift}px`;
        };

        let ticking = false;

        const onScroll = () => {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(() => {
                applyLogoSize(Math.max(0, tbNatural - (window.scrollY || window.pageYOffset)));
                ticking = false;
            });
        };

        window.addEventListener('scroll', onScroll, { passive: true });
        applyLogoSize(Math.max(0, tbNatural - (window.scrollY || window.pageYOffset)));
    }

    /* ── 2. Inline search ──────────────────────────────────────────────────── */

    const toggle     = document.getElementById('searchToggle');
    const closeBtn   = document.getElementById('searchClose');
    const input      = nav.querySelector('.nav-search-inline-input');
    const searchItem = nav.querySelector('.nav-search-item');

    if (!toggle || !closeBtn || !input || !searchItem) return;

    const openSearch = () => {
        nav.classList.remove('search-hover');
        nav.classList.add('search-open');
        toggle.setAttribute('aria-expanded', 'true');
        input.removeAttribute('tabindex');
        closeBtn.removeAttribute('tabindex');
        input.focus();
    };

    const openHover = () => {
        nav.classList.add('search-hover');
        input.removeAttribute('tabindex');
        closeBtn.removeAttribute('tabindex');
        input.focus();
    };

    const closeSearch = () => {
        nav.classList.remove('search-open', 'search-hover');
        toggle.setAttribute('aria-expanded', 'false');
        input.setAttribute('tabindex', '-1');
        closeBtn.setAttribute('tabindex', '-1');
        input.value = '';
    };

    /* Auto-cancel after 10 s of inactivity */
    let idleTimer = null;

    const resetIdleTimer = () => {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(closeSearch, 10_000);
    };

    const cancelIdleTimer = () => clearTimeout(idleTimer);

    /* Hover expand */
    let hoverCloseTimer = null;

    searchItem.addEventListener('mouseenter', () => {
        clearTimeout(hoverCloseTimer);
        cancelIdleTimer();
        if (!nav.classList.contains('search-open')) openHover();
    });

    searchItem.addEventListener('mouseleave', () => {
        /* Do not close while input is focused — browser autocomplete dropdown
           lives outside the DOM and fires mouseleave on the search item. */
        if (nav.classList.contains('search-open') || document.activeElement === input) return;
        if (input.value.trim() === '') {
            hoverCloseTimer = setTimeout(closeSearch, 200);
        } else {
            resetIdleTimer();
        }
    });

    input.addEventListener('input', () => {
        input.value.trim() ? resetIdleTimer() : cancelIdleTimer();
    });

    toggle.addEventListener('click', () => {
        nav.classList.contains('search-open') ? closeSearch() : openSearch();
    });

    closeBtn.addEventListener('click', closeSearch);

    /* Click outside — delay so browser autocomplete fill is captured first */
    document.addEventListener('click', (e) => {
        if (!nav.classList.contains('search-open') || searchItem.contains(e.target)) return;
        setTimeout(() => {
            if (input.value.trim() === '') closeSearch();
        }, 50);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('search-open')) closeSearch();
    });

})();
