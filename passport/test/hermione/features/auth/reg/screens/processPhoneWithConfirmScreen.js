const PO = require('../../../../page-objects/auth/reg');
const utils = require('../../../../utils/utils');

async function processPhoneWithConfirmScreen(browser) {
    await browser.yaWaitForVisible(PO.phoneScreen());

    await browser.yaSetValue(PO.phoneScreen.phoneInput(), utils.getRandomFakePhoneInE164());
    await browser.click(PO.phoneScreen.nextButton());

    await browser.yaWaitForVisible(PO.phoneConfirmationCodeScreen());

    const trackId = await browser.yaGetTrackId();
    const code = await utils.getPhoneConfirmationCode(trackId);

    await browser.yaSetValue(PO.phoneConfirmationCodeScreen.codeInput(), code);
}

module.exports = {
    processPhoneWithConfirmScreen
};
