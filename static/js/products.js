/**
 * GFI — Products JS
 *
 * Three behaviours:
 *
 * 1. Navigation (category links, filter checkboxes, Clear button)
 *    → Full section swap with fade animation, URL updated via pushState.
 *
 * 2. Live search (debounced input on the search bar)
 *    → Only replaces #products-grid contents, sidebar stays intact,
 *      input focus never lost.
 *
 * 3. Load More
 *    → Fetches next page of cards and appends to #products-grid.
 */

(() => {
    'use strict';

    const section = document.getElementById('products-section');
    if (!section) return;

    const FADE_OUT = 150;
    const FADE_IN  = 220;

    /* ------------------------------------------------------------------ */
    /* Full section swap                                                    */
    /* ------------------------------------------------------------------ */

    const swapContent = (html) => new Promise((resolve) => {
        section.classList.add('is-swapping');
        setTimeout(() => {
            section.innerHTML = html;
            void section.offsetHeight;
            section.classList.remove('is-swapping');
            setTimeout(resolve, FADE_IN);
        }, FADE_OUT);
    });

    const fetchAndSwap = (url) => {
        fetch(url, { headers: { 'X-GFI-Partial': '1' } })
            .then((res) => {
                if (!res.ok) throw new Error('bad response');
                return res.text();
            })
            .then(swapContent)
            .then(() => {
                history.pushState(null, '', url);
                bindAll();
            })
            .catch(() => { window.location.href = url; });
    };

    /* ------------------------------------------------------------------ */
    /* Build URLs                                                           */
    /* ------------------------------------------------------------------ */

    /**
     * Build a URL for a filter change (certification / application / origin).
     * Reads all currently-checked checkboxes/radios from the sidebar,
     * preserves the current search query, and resets to page 1.
     */
    const buildFilterUrl = () => {
        const url = new URL(window.location.href);
        url.searchParams.delete('cert');
        url.searchParams.delete('app');
        url.searchParams.delete('origin');
        url.searchParams.delete('page');

        section.querySelectorAll('.js-filter-cert:checked').forEach((cb) => {
            url.searchParams.append('cert', cb.value);
        });
        section.querySelectorAll('.js-filter-app:checked').forEach((cb) => {
            url.searchParams.append('app', cb.value);
        });
        const originRadio = section.querySelector('.js-filter-origin:checked');
        if (originRadio) url.searchParams.set('origin', originRadio.value);

        return url.toString();
    };

    /**
     * Build a URL for a search-input change.
     * Preserves all current filter params (cert / app / origin), resets page.
     */
    const buildSearchUrl = (form) => {
        const url = new URL(window.location.href);
        const q = form.querySelector('input[name="q"]').value.trim();
        if (q) url.searchParams.set('q', q);
        else url.searchParams.delete('q');
        url.searchParams.delete('page');
        return url.toString();
    };

    /* ------------------------------------------------------------------ */
    /* Load More                                                            */
    /* ------------------------------------------------------------------ */

    const bindLoadMore = () => {
        const btn = section.querySelector('.js-load-more');
        if (!btn) return;

        btn.addEventListener('click', () => {
            const nextPage = btn.dataset.nextPage;
            const url = new URL(window.location.href);
            url.searchParams.set('page', nextPage);

            btn.disabled = true;
            btn.textContent = '…';

            fetch(url.toString(), { headers: { 'X-GFI-Partial': 'cards' } })
                .then((res) => {
                    if (!res.ok) throw new Error('bad response');
                    return res.text();
                })
                .then((html) => {
                    const container = section.querySelector('#load-more-container');
                    if (container) container.remove();
                    const grid = section.querySelector('#products-grid');
                    if (grid) {
                        grid.insertAdjacentHTML('beforeend', html);
                        bindLoadMore();
                    }
                })
                .catch(() => { window.location.href = url.toString(); });
        });
    };

    /* ------------------------------------------------------------------ */
    /* Category sidebar text filter (client-side, no server request)       */
    /* ------------------------------------------------------------------ */

    const bindCategoryFilter = () => {
        const input = section.querySelector('#category-filter');
        const list  = section.querySelector('#category-list');
        if (!input || !list) return;

        /* Inject the no-match message element once */
        let noMatch = list.querySelector('.js-cat-no-match');
        if (!noMatch) {
            noMatch = document.createElement('li');
            noMatch.className = 'js-cat-no-match';
            noMatch.style.display = 'none';
            noMatch.innerHTML = '<span class="product-filter-panel__no-match">No categories match.</span>';
            list.appendChild(noMatch);
        }

        input.addEventListener('input', () => {
            const term = input.value.trim().toLowerCase();
            let visible = 0;
            list.querySelectorAll('li:not(.js-cat-no-match)').forEach((li) => {
                const matches = !term || li.textContent.trim().toLowerCase().includes(term);
                li.style.display = matches ? '' : 'none';
                if (matches) visible++;
            });
            noMatch.style.display = (term && visible === 0) ? '' : 'none';
        });
    };

    /* ------------------------------------------------------------------ */
    /* Bind everything                                                      */
    /* ------------------------------------------------------------------ */

    const bindAll = () => {

        /* Category links and Clear button */
        section.querySelectorAll('.js-filter-nav').forEach((el) => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                fetchAndSwap(el.getAttribute('href'));
            });
        });

        /* Search form submit */
        const form = section.querySelector('.js-product-search');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                fetchAndSwap(buildSearchUrl(form));
            });

            /* Live search — only updates #products-grid, preserves focus */
            let debounceTimer;
            const input = form.querySelector('input[name="q"]');
            if (input) {
                input.addEventListener('input', () => {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        const url = buildSearchUrl(form);
                        fetch(url, { headers: { 'X-GFI-Partial': 'cards' } })
                            .then((res) => {
                                if (!res.ok) throw new Error('bad response');
                                return res.text();
                            })
                            .then((html) => {
                                const grid = section.querySelector('#products-grid');
                                if (grid) grid.innerHTML = html;
                                history.replaceState(null, '', url);
                                bindLoadMore();
                            })
                            .catch(() => {});
                    }, 350);
                });
            }
        }

        /* Certification / Application checkboxes */
        section.querySelectorAll('.js-filter-cert, .js-filter-app').forEach((cb) => {
            cb.addEventListener('change', () => fetchAndSwap(buildFilterUrl()));
        });

        /* Origin radio buttons */
        section.querySelectorAll('.js-filter-origin').forEach((rb) => {
            rb.addEventListener('change', () => fetchAndSwap(buildFilterUrl()));
        });

        /* Clear origin button */
        const clearOrigin = section.querySelector('.js-clear-origin');
        if (clearOrigin) {
            clearOrigin.addEventListener('click', () => {
                section.querySelectorAll('.js-filter-origin').forEach((rb) => {
                    rb.checked = false;
                });
                fetchAndSwap(buildFilterUrl());
            });
        }

        bindLoadMore();
        bindCategoryFilter();
    };

    bindAll();

    window.addEventListener('popstate', () => fetchAndSwap(window.location.href));

})();
