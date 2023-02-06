import puppeteer from 'puppeteer';

import {PATH_TO_STORYBOOK} from '../../tests-bootstrap';

const BUTTONS_QUERY = 'id=blank-ui-button--button&viewMode=story';

describe('button', () => {
    it(`button page should render the same`, async () => {
        let browser;

        try {
            browser = await puppeteer.launch();

            const page = await browser.newPage();
            page.setDefaultTimeout(0);

            await page.goto(`${PATH_TO_STORYBOOK}?${BUTTONS_QUERY}`, {
                waitUntil: 'networkidle2',
                timeout: 0,
            });
            await page.setViewport({width: 1920, height: 1080});

            const screenshot = await page.screenshot();

            expect(screenshot).toMatchImageSnapshot();
        } finally {
            if (browser) await browser.close();
        }
    });
});
