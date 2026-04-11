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

    /* ── 2. Mobile search bar ─────────────────────────────────────────────── */

    const mobileSearchBtn = document.getElementById('mobileSearchBtn');
    const mobileSearchBar = document.getElementById('mobileSearchBar');
    const mobileSearchInput = document.getElementById('mobileSearchInput');
    const collapseEl = document.getElementById('gfiNavbar');

    if (mobileSearchBtn && mobileSearchBar && mobileSearchInput) {
        const openMobileSearch = () => {
            mobileSearchBar.classList.add('is-open');
            mobileSearchBar.setAttribute('aria-hidden', 'false');
            mobileSearchBtn.setAttribute('aria-expanded', 'true');
            mobileSearchInput.focus();
            // Close burger menu if open
            if (collapseEl && collapseEl.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(collapseEl);
                if (bsCollapse) bsCollapse.hide();
            }
        };

        const closeMobileSearch = () => {
            mobileSearchBar.classList.remove('is-open');
            mobileSearchBar.setAttribute('aria-hidden', 'true');
            mobileSearchBtn.setAttribute('aria-expanded', 'false');
        };

        mobileSearchBtn.addEventListener('click', () => {
            mobileSearchBar.classList.contains('is-open') ? closeMobileSearch() : openMobileSearch();
        });

        // Close mobile search when burger menu is shown
        collapseEl?.addEventListener('show.bs.collapse', closeMobileSearch);

        // ESC to close
        mobileSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeMobileSearch();
                mobileSearchBtn.focus();
            }
        });
    }

    /* ── 3. Inline search (desktop) ───────────────────────────────────────── */

    const toggle     = document.getElementById('searchToggle');
    const closeBtn   = document.getElementById('searchClose');
    const input      = nav.querySelector('.nav-search-inline-input');
    const searchItem = nav.querySelector('.nav-search-item');
    const dropdown   = document.getElementById('searchDropdown');
    const form       = nav.querySelector('.nav-search-inline');

    if (!toggle || !closeBtn || !input || !searchItem || !dropdown || !form) return;

    const suggestUrl = form.dataset.suggestUrl;

    /* ── State ─────────────────────────────────────────────────────────────── */

    let lastResults   = { categories: [], products: [] };
    let debounceTimer = null;
    let idleTimer     = null;
    let hoverCloseTimer = null;

    /* ── Open / close ──────────────────────────────────────────────────────── */

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

    const hideDropdown = () => {
        dropdown.classList.remove('nav-search-dropdown--visible');
        dropdown.innerHTML = '';
    };

    const closeSearch = () => {
        nav.classList.remove('search-open', 'search-hover');
        toggle.setAttribute('aria-expanded', 'false');
        input.setAttribute('tabindex', '-1');
        closeBtn.setAttribute('tabindex', '-1');
        input.value = '';
        hideDropdown();
    };

    /* ── Idle timer ────────────────────────────────────────────────────────── */

    const resetIdleTimer = () => {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(closeSearch, 10_000);
    };

    const cancelIdleTimer = () => clearTimeout(idleTimer);

    /* ── Dropdown rendering ────────────────────────────────────────────────── */

    const buildRow = (label, sublabel, url, iconClass) => {
        const a = document.createElement('a');
        a.href = url;
        a.className = 'nav-search-row';
        a.setAttribute('role', 'option');

        const icon = document.createElement('i');
        icon.className = iconClass;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'nav-search-row__name';
        nameSpan.textContent = label;

        a.appendChild(icon);
        a.appendChild(nameSpan);

        if (sublabel) {
            const subSpan = document.createElement('span');
            subSpan.className = 'nav-search-row__sub';
            subSpan.textContent = sublabel;
            a.appendChild(subSpan);
        }

        return a;
    };

    const renderResults = (data) => {
        lastResults = data;
        dropdown.innerHTML = '';

        const { categories, products } = data;

        if (categories.length === 0 && products.length === 0) {
            const msg = document.createElement('p');
            msg.className = 'nav-search-empty';
            msg.textContent = nav.dataset.noMatch || 'No matches found';
            dropdown.appendChild(msg);
            dropdown.classList.add('nav-search-dropdown--visible');
            return;
        }

        if (categories.length) {
            const hdr = document.createElement('p');
            hdr.className = 'nav-search-group';
            hdr.textContent = nav.dataset.labelCategories || 'Categories';
            dropdown.appendChild(hdr);
            categories.forEach(c => dropdown.appendChild(buildRow(c.name, null, c.url, 'bi bi-grid-3x3-gap')));
        }

        if (products.length) {
            const hdr = document.createElement('p');
            hdr.className = 'nav-search-group';
            hdr.textContent = nav.dataset.labelProducts || 'Products';
            dropdown.appendChild(hdr);
            products.forEach(p => dropdown.appendChild(buildRow(p.name, p.category, p.url, 'bi bi-box-seam')));
        }

        dropdown.classList.add('nav-search-dropdown--visible');
    };

    /* ── Fetch suggestions (debounced) ─────────────────────────────────────── */

    const fetchSuggestions = (q) => {
        clearTimeout(debounceTimer);
        if (q.length < 2) { hideDropdown(); return; }
        debounceTimer = setTimeout(async () => {
            try {
                const res  = await fetch(`${suggestUrl}?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                renderResults(data);
            } catch (_) { /* network error — fail silently */ }
        }, 220);
    };

    /* ── Enter-key smart routing ───────────────────────────────────────────── */

    const handleEnter = (e) => {
        if (e.key !== 'Enter') return;
        e.preventDefault();

        const { categories, products } = lastResults;
        const total = categories.length + products.length;

        if (total === 0) {
            /* nothing found — stay, keep showing dropdown */
            return;
        }

        if (categories.length === 1 && products.length === 0) {
            window.location.href = categories[0].url;
            return;
        }

        if (products.length === 1 && categories.length === 0) {
            window.location.href = products[0].url;
            return;
        }

        /* multiple results — go to product list with search query */
        const q = input.value.trim();
        if (q) {
            window.location.href = `${form.action}?q=${encodeURIComponent(q)}`;
        }
    };

    /* ── Event wiring ──────────────────────────────────────────────────────── */

    input.addEventListener('input', () => {
        const q = input.value.trim();
        if (q) {
            fetchSuggestions(q);
            resetIdleTimer();
        } else {
            hideDropdown();
            cancelIdleTimer();
        }
    });

    input.addEventListener('keydown', handleEnter);

    toggle.addEventListener('click', () => {
        nav.classList.contains('search-open') ? closeSearch() : openSearch();
    });

    closeBtn.addEventListener('click', closeSearch);

    /* Hover expand */
    searchItem.addEventListener('mouseenter', () => {
        clearTimeout(hoverCloseTimer);
        cancelIdleTimer();
        if (!nav.classList.contains('search-open')) openHover();
    });

    searchItem.addEventListener('mouseleave', () => {
        if (nav.classList.contains('search-open') || document.activeElement === input) return;
        if (input.value.trim() === '') {
            hoverCloseTimer = setTimeout(closeSearch, 200);
        } else {
            resetIdleTimer();
        }
    });

    /* Click outside */
    document.addEventListener('click', (e) => {
        if (!nav.classList.contains('search-open') || searchItem.contains(e.target)) return;
        setTimeout(() => {
            if (input.value.trim() === '') closeSearch();
            else hideDropdown();
        }, 50);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('search-open')) closeSearch();
    });

})();
