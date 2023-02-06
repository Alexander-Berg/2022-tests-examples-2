const {expect} = require('chai');
const pages = require('../../utils/passportPages');
const {registrationSocialButtons} = require('../../page-objects/auth/reg');

describe('/restoration/form socialButtons', function() {
    it('should show facebook social button with exp: social-provider-fb-exp', async function() {
        await this.browser.url(`${pages.AUTH_REG.getUrl()}?origin=serp&flag-ids=social-provider-fb-exp`);
        await this.browser.waitForExist(registrationSocialButtons());
        await this.browser.waitForExist(registrationSocialButtons.registrationFBButton());
    });
    it('should hidden facebook social button without exp: social-provider-fb-exp', async function() {
        await this.browser.url(`${pages.AUTH_REG.getUrl()}?origin=serp`);
        await this.browser.waitForExist(registrationSocialButtons());
        expect(await this.browser.isVisible(registrationSocialButtons.registrationFBButton())).to.equal(false);
    });
});
