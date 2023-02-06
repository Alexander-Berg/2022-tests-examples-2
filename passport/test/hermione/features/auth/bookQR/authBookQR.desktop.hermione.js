const expect = require('chai').expect;
const {getRandomPassword, getRandomFreeLogin} = require('../../../utils/utils');
const {createEmptyUser, createUserWithOPT, createUserWithPhone} = require('../../../helpers/api/passport/registration');
const {authOtpPrepare} = require('../../../helpers/api/passport/auth');
const {confirmQR, getTrackIdFromQR} = require('../../../helpers/api/passport/confirmQR');
const pages = require('../../../utils/passportPages');
const bookQRPO = require('../../../page-objects/auth/bookQR');
const welcomePO = require('../../../page-objects/auth/welcome');
const {processOtpQR} = require('../../../helpers/api/passport/processOtpQR');
const {tryDeleteAccountAfterRun} = require('../../../helpers/api/passport/delete');

async function processCaptchaScreen(browser) {
    await browser.yaWaitForVisible(bookQRPO.captchaScreen());
    await browser.yaPassCaptcha(
        bookQRPO.captchaScreen.key(),
        bookQRPO.captchaScreen.input(),
        bookQRPO.captchaScreen.button()
    );
}

async function getTrackId(browser) {
    const element = await browser.$(bookQRPO.magicBookPage.qr());
    const trackId = await getTrackIdFromQR(element);

    return trackId;
}

async function processQR(browser, user) {
    await browser.yaShouldBeVisible(bookQRPO.magicBookPage());
    const trackId = await getTrackId(browser);

    await confirmQR(trackId, user.login, user.password);
}

async function checkIsProfilePage(browser) {
    await browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
    await browser.yaShouldBeAtUrl(pages.PROFILE);
}

async function bruteForceOtpQR(browser, login) {
    for (let i = 0; i < 10; i++) {
        try {
            const trackId = await getTrackId(browser);

            await authOtpPrepare(login, getRandomPassword(), trackId);
            await browser.pause(500);
        } catch (error) {
            i = 10;
        }
    }
}

const TEST_ID = 478175;

describe('/auth', () => {
    describe('bookQR experiment', () => {
        it('should show book under experiment', async function() {
            await this.browser.url(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
            await this.browser.yaShouldBeVisible(this.PO.auth());
            await this.browser.yaShouldBeVisible(this.PO.auth.loginInput());
            await this.browser.yaShouldBeVisible(bookQRPO.magicBookPage());
        });
        it(
            'should login with qr',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.url(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
                await this.browser.yaShouldBeAtUrl(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);

                const user = await createEmptyUser();

                await processQR(this.browser, user);
                await checkIsProfilePage(this.browser);
            })
        );
        it(
            'should login with qr with requested user',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.url(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
                await this.browser.yaShouldBeAtUrl(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);

                const user = await createEmptyUser();

                await processQR(this.browser, user);
                await checkIsProfilePage(this.browser);

                await this.browser.url(`${pages.AUTH.getUrl()}?login=${user.login}&test-id=${TEST_ID}`);
                await this.browser.yaShouldBeAtUrl(
                    `${pages.AUTH_WELCOME.getUrl()}?login=${user.login}&test-id=${TEST_ID}`
                );
                await this.browser.yaShouldBeVisible(welcomePO.welcomeScreen());
                await this.browser.click(welcomePO.welcomeScreen.currentAccount());
                await this.browser.yaShouldBeVisible(bookQRPO.authAccountListScreen());
                await this.browser.yaShouldBeVisible(bookQRPO.authAccountListScreen.listButton());
                await this.browser.click(bookQRPO.authAccountListScreen.addButton());

                await this.browser.pause(2000);

                await processQR(this.browser, user);
                await checkIsProfilePage(this.browser);
            })
        );
        it(
            'should login with qr and captcha',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.url(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
                await this.browser.yaShouldBeAtUrl(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);

                const {user, secret} = await createUserWithOPT();

                await this.browser.yaShouldBeVisible(bookQRPO.magicBookPage());

                await bruteForceOtpQR(this.browser, user.login);

                await processCaptchaScreen(this.browser);
                await this.browser.yaShouldBeVisible(bookQRPO.magicBookPage());

                const trackId = await getTrackId(this.browser);

                await processOtpQR(user, secret, trackId);
                await checkIsProfilePage(this.browser);
            })
        );
        hermione.skip.in(/.*/, 'Нужно научится вызывать челендж');
        it.skip(
            'should login with qr and challenge',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.url(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);
                await this.browser.yaShouldBeAtUrl(`${pages.AUTH.getUrl()}?test-id=${TEST_ID}`);

                const user = await createUserWithPhone({login: await getRandomFreeLogin('yndx-profile-test-')});

                await processQR(this.browser, user);
                await checkIsProfilePage(this.browser);
            })
        );
    });
    describe('without experiment', () => {
        it('should not show book for custom', async function() {
            await this.browser.url(`${pages.AUTH.getUrl()}?test-id=478175&origin=serp_disk`);
            const isVisible = await this.browser.isVisible(bookQRPO.magicBookPage());

            expect(isVisible).to.equal(false);
        });
    });
});
