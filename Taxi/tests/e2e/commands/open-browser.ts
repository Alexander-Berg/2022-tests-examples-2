import puppeteer, {Browser} from 'puppeteer';

let browser: Browser;

const windowWidth = 1680;
const windowHeight = 927;

async function openBrowser() {
    browser = await puppeteer.connect({
        browserURL: `http://localhost:${process.env.CHROMIUM_PORT}`,
        slowMo: 80,
        defaultViewport: {
            width: windowWidth,
            height: windowHeight
        }
    });

    return browser;
}

async function closeBrowser() {
    browser.disconnect();
}

export {openBrowser, closeBrowser, browser, windowWidth, windowHeight};
