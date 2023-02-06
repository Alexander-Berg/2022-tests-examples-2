const PO = require('../../../../page-objects/auth/reg');
const {pageOverlay} = require('../../../../page-objects/auth');

async function processCaptchaScreen(browser) {
    await browser.yaWaitForVisible(PO.captchaScreen());
    await browser.yaWaitUntil(
        'pageOverlay.loader still visible',
        async () => !(await browser.isVisible(pageOverlay.loader()))
    );
    await browser.yaWaitForVisible(PO.captchaScreen.input());
    await browser.yaWaitForVisible(PO.captchaScreen.nextButton());
    await browser.yaPassCaptcha(PO.captchaScreen.captchaKey(), PO.captchaScreen.input(), PO.captchaScreen.nextButton());
}

module.exports = {
    processCaptchaScreen
};
