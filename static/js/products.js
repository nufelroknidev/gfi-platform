/**
 * GFI — Products
 *
 * Intercepts category links and the search form on the product pages.
 * Fetches only the products grid fragment and swaps it in place with a
 * fade-out → swap → fade-in animation. Falls back to normal navigation
 * if the fetch fails.
 *
 * Works on both the category list page (list.html) and the category
 * detail page (category.html) — any page that has #products-section.
 *
 * Animation is driven by the .is-swapping CSS class (see products.css).
 * JS only toggles state; the transition values live in the stylesheet.
 */

(() => {
    'use strict';

    const section = document.getElementById('products-section');
    if (!section) return;

    /* Must match the transition duration on .is-swapping in products.css */
    const FADE_OUT = 150;  /* ms */
    const FADE_IN  = 220;  /* ms */

    const swapContent = (html) => new Promise((resolve) => {
        section.classList.add('is-swapping');

        setTimeout(() => {
            section.innerHTML = html;

            /* Force a reflow so the browser registers the hidden state
               before the transition back to visible begins. */
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
                bindLinks();
            })
            .catch(() => {
                window.location.href = url;
            });
    };

    const bindLinks = () => {
        section.querySelectorAll('.js-category-link').forEach((el) => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                fetchAndSwap(el.getAttribute('href'));
            });
        });

        const form = section.querySelector('.js-product-search');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const url    = form.getAttribute('action') || window.location.pathname;
                const params = new URLSearchParams(new FormData(form)).toString();
                fetchAndSwap(url + (params ? `?${params}` : ''));
            });
        }
    };

    bindLinks();

    window.addEventListener('popstate', () => fetchAndSwap(window.location.href));

})();
