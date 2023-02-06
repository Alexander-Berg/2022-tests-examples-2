const pages = require('../../utils/passportPages');
const desktopPO = require('../../page-objects/desktop');
const {welcomeScreen, PhoneConfirmationCode} = require('../../page-objects/auth/welcome');
const {readTrack} = require('../../helpers/api/passport/track');
const {delay} = require('../../utils/utils');

const WAIT_BEFORE_CLICK_TIMEOUT = 1000;

async function processAuthNeophonish(browser, user) {
    await browser.url(`${pages.AUTH.getUrl()}`);
    await browser.yaSetValue(desktopPO.auth.loginInput(), user.phones.secure);
    await browser.click(desktopPO.submitButton());

    await browser.yaWaitForVisible(welcomeScreen.authPasswordForm());
    const trackId = await browser.getValue(welcomeScreen.authPasswordForm.hiddenTrackId());

    await delay(WAIT_BEFORE_CLICK_TIMEOUT);
    await browser.click(welcomeScreen.authBySMS());
    await browser.yaWaitForVisible(PhoneConfirmationCode.phoneCodeInput());
    const {phone_confirmation_code} = await readTrack(trackId);

    await browser.yaSetValue(PhoneConfirmationCode.phoneCodeInput(), phone_confirmation_code);
    // await browser.click(PhoneConfirmationCode.nextButton());
    await browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
    await browser.yaShouldBeAtUrl(pages.PROFILE);
}

module.exports = {
    processAuthNeophonish
};
