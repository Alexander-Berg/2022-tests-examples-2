const {expect} = require('chai');
const steps = require('../../helpers/api/steps');
const {tryDeleteAccountAfterRun} = require('../../helpers/api/passport/delete');
const {addProfile, sectionSocial, sectionSocialModal} = require('../../page-objects/profile');
const pages = require('../../utils/passportPages');

describe('/profile socialButtons', function() {
    it(
        'should show facebook social button with exp: social-provider-fb-exp',
        tryDeleteAccountAfterRun(async function() {
            const user = await steps.passport.registration.createEmptyUser();

            await this.browser.yaAuth(user);
            await this.browser.url(`${pages.PROFILE.getUrl()}?flag-ids=social-provider-fb-exp`);
            await this.browser.waitForExist(sectionSocial());
            await this.browser.click(sectionSocial());
            await this.browser.click(sectionSocial.link());
            await this.browser.waitForExist(sectionSocialModal());
            await this.browser.waitForExist(addProfile());
            await this.browser.waitForExist(addProfile.socialIconFB());
        })
    );
    it(
        'should hidden facebook social button without exp: social-provider-fb-exp',
        tryDeleteAccountAfterRun(async function() {
            const user = await steps.passport.registration.createEmptyUser();

            await this.browser.yaAuth(user);
            await this.browser.url(pages.PROFILE.getUrl());
            await this.browser.waitForExist(sectionSocial());
            await this.browser.click(sectionSocial());
            await this.browser.click(sectionSocial.link());
            await this.browser.waitForExist(sectionSocialModal());
            await this.browser.waitForExist(addProfile());
            expect(await this.browser.isVisible(addProfile.socialIconFB())).to.equal(false);
        })
    );
});
