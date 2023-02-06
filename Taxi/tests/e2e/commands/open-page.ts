import {browser} from './open-browser';
import {setTestStyles, SetTestStylesOptions} from './set-styles';

type OpenPageOptions = SetTestStylesOptions;

async function openPage(path: string, options?: OpenPageOptions) {
    const page = await browser.newPage();

    await page.goto(`${process.env.TEST_DOMAIN}/${path}`);
    await setTestStyles(page, options);

    return page;
}

async function openIncognitoPage(path: string, options?: OpenPageOptions) {
    const context = await browser.createIncognitoBrowserContext();
    const page = await context.newPage();

    await page.goto(`${process.env.TEST_DOMAIN}/${path}`);
    await setTestStyles(page, options);

    return {page, context};
}

export {openPage, openIncognitoPage};
