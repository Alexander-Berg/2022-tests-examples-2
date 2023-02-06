const utils = require('../utils/utils');
const pages = require('../utils/passportPages');

describe('challenge as a service', function() {
    beforeEach(async function() {
        await this.browser.yaAuth('yndx-howl');
        await this.browser.url(pages.AUTH_USER_VALIDATE.getUrl());
    });

    it('should open user challenge page', async function() {
        await this.browser.yaShouldHaveVisibleText(
            '.auth-challenge-descr',
            'Пожалуйста, подтвердите номер телефона, который привязан к вашему аккаунту.'
        );
    });

    it('should send sms to user number', async function() {
        const PO = this.PO;

        await this.browser.yaShouldBeVisible(PO.submitButton());
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldHaveVisibleText(
            PO.auth.title(),
            'Введите код из СМС, отправленный на номер\n+7 000 ***-**-07'
        );
    });

    it('should check code and redirect to profile', async function() {
        const PO = this.PO;

        await this.browser.click(PO.submitButton());

        await this.browser.waitForExist(PO.challenge.phoneCodeInput(), 2000);
        const trackId = await this.browser.yaGetTrackId();
        const code = await utils.getPhoneConfirmationCode(trackId);

        await this.browser.yaSetValue(PO.challenge.phoneCodeInput(), code);
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldBeAtUrl(pages.PROFILE);
    });

    it('should show error with wrong code', async function() {
        const PO = this.PO;

        await this.browser.click(PO.submitButton());

        await this.browser.yaSetValue(PO.challenge.phoneCodeInput(), 'bad_code');
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldHaveVisibleText(PO.auth.errorField, 'Неправильный код подтверждения');
    });
});
