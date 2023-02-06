const {expect} = require('chai');
const pages = require('../../../../utils/passportPages');
const PO = require('../../../../page-objects/auth/reg');
const {processAuthSocial} = require('../../processAuthSocial');
const {tryDeleteAccountAfterRun, deleteAccount, getUserId} = require('../../../../helpers/api/passport/delete');
const {
    processCaptchaScreen,
    processPasswordScreen,
    processPersonalDataScreen,
    processSqSaScreen,
    processLoginScreen,
    processPhoneWithConfirmScreen
} = require('../screens');
const {delay} = require('../../../../utils/utils');

describe('/auth/complete', function() {
    describe('complete_social_with_login for default configs', function() {
        it(
            'should complete registration',
            tryDeleteAccountAfterRun(async function() {
                await processAuthSocial(this.browser);
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?test-id=00`);
                await this.browser.waitUntil(() => this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl()));
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await this.browser.click(PO.phoneScreen.switchButton());
                await processSqSaScreen(this.browser);
                await processCaptchaScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
            })
        );
        it(
            'should complete registration with phone',
            tryDeleteAccountAfterRun(async function() {
                await processAuthSocial(this.browser);
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?test-id=00`);
                await this.browser.waitUntil(() => this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl()));
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await processPhoneWithConfirmScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
            })
        );
    });
    describe('complete_social_with_login for test origin', function() {
        it(
            'should complete registration',
            tryDeleteAccountAfterRun(async function() {
                await processAuthSocial(this.browser);
                await this.browser.url(
                    `${pages.AUTH_REG_COMPLETE.getUrl()}?test-id=00&origin=test_noPersonalData_regComplete`
                );
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processLoginScreen(this.browser);
                await this.browser.click(PO.phoneScreen.switchButton());
                await processSqSaScreen(this.browser);
                await processCaptchaScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
            })
        );
        it(
            'should complete registration with phone',
            tryDeleteAccountAfterRun(async function() {
                await processAuthSocial(this.browser);
                await this.browser.url(
                    `${pages.AUTH_REG_COMPLETE.getUrl()}?test-id=00&origin=test_noPersonalData_regComplete`
                );
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processLoginScreen(this.browser);
                await processPhoneWithConfirmScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
            })
        );
    });
    describe('on /am?app_platform=android&mode=upgrade', function() {
        it('should complete complete_social_with_login process for default configs', async function() {
            let error;

            let userId;

            try {
                await processAuthSocial(this.browser);
                userId = await getUserId(this.browser);

                await this.browser.url(`${pages.AM.getUrl()}?app_platform=android&mode=upgrade`);
                await delay(2000);
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());

                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await this.browser.click(PO.phoneScreen.switchButton());
                await processSqSaScreen(this.browser);
                await processCaptchaScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaShouldBeAtUrl(`${pages.AM.getUrl()}/finish?status=ok`);
            } catch (e) {
                error = e;
            }

            await deleteAccount(userId);

            if (error) {
                throw error;
            }
        });
        it('should complete complete_social_with_login process for default configs with phone', async function() {
            let error;

            let userId;

            try {
                await processAuthSocial(this.browser);
                userId = await getUserId(this.browser);

                await this.browser.url(`${pages.AM.getUrl()}?app_platform=android&mode=upgrade`);
                await delay(2000);
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());

                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await processPhoneWithConfirmScreen(this.browser);
                await processPasswordScreen(this.browser);
                await delay(2000);
                await this.browser.yaShouldBeAtUrl(`${pages.AM.getUrl()}/finish?status=ok`);
            } catch (e) {
                error = e;
            }

            await deleteAccount(userId);

            if (error) {
                throw error;
            }
        });
    });
    describe('complete_social_with_login with phoneConfirmationRequired', function() {
        it(
            'should hide noPhone button',
            tryDeleteAccountAfterRun(async function() {
                await processAuthSocial(this.browser);
                await this.browser.url(
                    `${pages.AUTH_REG_COMPLETE.getUrl()}?test-id=00&origin=test_phoneConfirmationRequired_regComplete`
                );
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await this.browser.yaWaitForVisible(PO.phoneScreen());
                expect(await this.browser.isVisible(PO.phoneScreen.switchButton())).to.equal(false);
            })
        );
    });
});
