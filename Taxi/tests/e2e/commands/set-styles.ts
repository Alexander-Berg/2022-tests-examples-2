import type {Page} from 'puppeteer';

export interface SetTestStylesOptions {
    headerStyleOff?: boolean;
}

export async function setTestStyles(page: Page, options: SetTestStylesOptions = {}) {
    const serializableOptions = {
        headerStyleOff: options.headerStyleOff || false
    };

    await page.evaluate((options) => {
        const ANIMATION_DISABLE_STYLE = `
            *,
            *::after,
            *::before {
                transition-delay: 0s !important;
                transition-duration: 0s !important;
                animation-delay: 0s !important;
                animation-duration: 0s !important;
                animation-play-state: paused !important;
            }
        `;

        const HEADER_STATIC_STYLE = '[data-testid="header"]{position: static !important;}';
        const REACT_QUERY_DEV_TOOLS_STYLE = '.ReactQueryDevtools{display: none !important;}';

        const style = document.createElement('style');

        style.innerHTML = ANIMATION_DISABLE_STYLE + REACT_QUERY_DEV_TOOLS_STYLE;
        if (!options.headerStyleOff) {
            style.innerHTML += HEADER_STATIC_STYLE;
        }

        document.getElementsByTagName('head')[0].appendChild(style);
    }, serializableOptions);
}
