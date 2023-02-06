const pages = require('../../../../utils/passportPages');
const PO = require('../../../../page-objects/auth/reg');
const {tryDeleteAccountAfterRun} = require('../../../../helpers/api/passport/delete');
const {deleteAccount} = require('../../../../helpers/api/passport/delete');
const {createLiteUser, createSuperLiteUser} = require('../../../../helpers/api/passport/registration');
const {setInputValue} = require('../../../../helpers/ui');
const {
    processCaptchaScreen,
    processCurrentPasswordScreen,
    processLoginScreen,
    processPasswordScreen,
    processPersonalDataScreen,
    processSqSaScreen,
    processPhoneWithConfirmScreen
} = require('../screens');
const {setAuthCookiesByUid} = require('../../setAuthCookiesByUid');

describe('/auth/complete', function() {
    describe('complete_lite for default configs', function() {
        it('should complete registration when user with password', async function() {
            const user = await createLiteUser();

            await this.browser.yaAuth(user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
            await processPersonalDataScreen(this.browser);
            await processLoginScreen(this.browser);
            await this.browser.click(PO.phoneScreen.switchButton());
            await processSqSaScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await processCurrentPasswordScreen(this.browser, user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration with phone when user with password', async function() {
            const user = await createLiteUser();

            await this.browser.yaAuth(user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
            await processPersonalDataScreen(this.browser);
            await processLoginScreen(this.browser);
            await processPhoneWithConfirmScreen(this.browser);
            await processCurrentPasswordScreen(this.browser, user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration when user without password', async function() {
            const user = await createSuperLiteUser();

            await setAuthCookiesByUid(this.browser, user.uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
            await processPersonalDataScreen(this.browser);
            await processLoginScreen(this.browser);
            await this.browser.click(PO.phoneScreen.switchButton());
            await processSqSaScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await processPasswordScreen(this.browser);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration with phone when user without password', async function() {
            const user = await createSuperLiteUser();

            await setAuthCookiesByUid(this.browser, user.uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
            await processPersonalDataScreen(this.browser);
            await processLoginScreen(this.browser);
            await processPhoneWithConfirmScreen(this.browser);
            await processPasswordScreen(this.browser);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it(
            'should show error on phone screen if phone incorrect',
            tryDeleteAccountAfterRun(async function() {
                const user = await createLiteUser();

                await this.browser.yaAuth(user);
                await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);

                await this.browser.yaWaitForVisible(PO.phoneScreen());
                await this.browser.yaSetValue(PO.phoneScreen.phoneInput(), '+700098468326285698582956985619856894568');
                await this.browser.click(PO.phoneScreen.nextButton());
                await this.browser.yaWaitForVisible(PO.phoneScreen.hint());
                await this.browser.yaShouldHaveVisibleText(PO.phoneScreen.hint());
                await this.browser.click(PO.phoneScreen.nextButton());
                await this.browser.yaWaitForVisible(PO.phoneScreen());
                await this.browser.yaShouldHaveVisibleText(PO.phoneScreen.hint());
            })
        );
        it(
            'should show error on current password screen if password incorrect',
            tryDeleteAccountAfterRun(async function() {
                const user = await createLiteUser();

                await this.browser.yaAuth(user);
                await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await processPhoneWithConfirmScreen(this.browser);

                await this.browser.yaWaitForVisible(PO.currentPasswordScreen());
                this.browser.$(PO.currentPasswordScreen.passwordInput()).clearValue();
                setInputValue(this.browser, PO.currentPasswordScreen.passwordInput(), 'lkbvaeruig384giwf487g');
                await this.browser.yaWaitForVisible(PO.currentPasswordScreen.nextButton());
                await this.browser.click(PO.currentPasswordScreen.nextButton());
                await this.browser.yaWaitForVisible(PO.currentPasswordScreen.hint());
                await this.browser.yaShouldHaveVisibleText(PO.currentPasswordScreen.hint());
                await this.browser.yaWaitForVisible(PO.currentPasswordScreen.nextButton());
                await this.browser.click(PO.currentPasswordScreen.nextButton());
                await this.browser.yaWaitForVisible(PO.currentPasswordScreen());
                await this.browser.yaShouldHaveVisibleText(PO.currentPasswordScreen.hint());
            })
        );
    });
    describe('complete_lite for test origin', function() {
        it('should complete registration when user with password', async function() {
            const user = await createLiteUser();

            await this.browser.yaAuth(user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?origin=test_noPersonalData_regComplete`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
            await processLoginScreen(this.browser);
            await this.browser.click(PO.phoneScreen.switchButton());
            await processSqSaScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await processCurrentPasswordScreen(this.browser, user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration with phone when user with password', async function() {
            const user = await createLiteUser();

            await this.browser.yaAuth(user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?origin=test_noPersonalData_regComplete`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
            await processLoginScreen(this.browser);
            await processPhoneWithConfirmScreen(this.browser);
            await processCurrentPasswordScreen(this.browser, user);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration when user without password', async function() {
            const user = await createSuperLiteUser();

            await setAuthCookiesByUid(this.browser, user.uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?origin=test_noPersonalData_regComplete`);
            await processLoginScreen(this.browser);
            await this.browser.click(PO.phoneScreen.switchButton());
            await processSqSaScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await processPasswordScreen(this.browser);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
        it('should complete registration with phone when user without password', async function() {
            const user = await createSuperLiteUser();

            await setAuthCookiesByUid(this.browser, user.uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?origin=test_noPersonalData_regComplete`);
            await processLoginScreen(this.browser);
            await processPhoneWithConfirmScreen(this.browser);
            await processPasswordScreen(this.browser);
            await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());

            await deleteAccount(user.uid);
        });
    });
});
