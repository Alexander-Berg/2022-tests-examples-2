const pages = require('../../utils/passportPages');
const desktopPO = require('../../page-objects/desktop');
const authPO = require('../../page-objects/auth');
const {welcomeScreen, PhoneConfirmationCode} = require('../../page-objects/auth/welcome');
const {setInputValue} = require('../../helpers/ui');
const {getRandomFakePhoneInE164, delay} = require('../../utils/utils');
const {readTrack} = require('../../helpers/api/passport/track');

const WAIT_BEFORE_CLICK_TIMEOUT = 1000;

// TODO Нужно разобраться как кейс воспроизводить c нового номера
describe.skip('/auth', () => {
    it('Should start reg neophonish', async function() {
        await this.browser.url(
            `${pages.AUTH.getUrl()}?flag-ids=domik-phone-autostart-on%3Buse-new-suggest-by-phone&test-id=00`
        );
        const phone = await getRandomFakePhoneInE164();

        await setInputValue(this.browser, desktopPO.auth.loginInput(), phone);
        await this.browser.click(desktopPO.submitButton());

        await this.browser.yaWaitForVisible(PhoneConfirmationCode());
        const trackId = await this.browser.yaGetTrackId();

        await this.browser.yaWaitForVisible(PhoneConfirmationCode.phoneCodeInput());
        const {phone_confirmation_code} = await readTrack(trackId);

        await setInputValue(this.browser, PhoneConfirmationCode.phoneCodeInput(), phone_confirmation_code);

        await this.browser.yaWaitForVisible(authPO.accountsScreen());
    });
    it('Should restore neophonish', async function() {
        const flags = ['domik-phone-autostart-on', 'domik-neophonish-exp-enable', 'use-new-suggest-by-phone'].join(
            '%3B'
        );
        const qs = `flag-ids=${flags}&test-id=00&origin=neophonish`;

        await this.browser.url(`${pages.AUTH.getUrl()}?${qs}`);
        const phone = await getRandomFakePhoneInE164();

        await setInputValue(this.browser, desktopPO.auth.loginInput(), phone);
        await this.browser.click(desktopPO.submitButton());

        await this.browser.yaWaitForVisible(PhoneConfirmationCode());
        const trackId = await this.browser.yaGetTrackId();

        await delay(WAIT_BEFORE_CLICK_TIMEOUT);
        await this.browser.click(welcomeScreen.authBySMS());
        await this.browser.yaWaitForVisible(PhoneConfirmationCode.phoneCodeInput());
        const {phone_confirmation_code} = await readTrack(trackId);

        await setInputValue(this.browser, PhoneConfirmationCode.phoneCodeInput(), phone_confirmation_code);

        await this.browser.yaWaitForVisible(authPO.accountsScreen());
    });
});
