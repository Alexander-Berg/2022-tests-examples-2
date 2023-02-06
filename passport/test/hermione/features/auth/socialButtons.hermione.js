const {expect} = require('chai');
const pages = require('../../utils/passportPages');
const {listScreen} = require('../../page-objects/auth');
const {authSocialBlock} = require('../../page-objects/auth');

describe('/auth socialButtons', function() {
    it('should show facebook social button with exp: social-provider-fb-exp', async function() {
        await this.browser.url(`${pages.AUTH_ADD.getUrl()}?flag-ids=social-provider-fb-exp`);
        if (await this.browser.isVisible(listScreen())) {
            await this.browser.click(listScreen.listItemAddButton());
        }
        await this.browser.waitForExist(authSocialBlock());
        await this.browser.waitForExist(authSocialBlock.providerPrimaryFB());
    });
    it('should hidden facebook social button without exp: social-provider-fb-exp', async function() {
        await this.browser.url(pages.AUTH_ADD.getUrl());
        if (await this.browser.isVisible(listScreen())) {
            await this.browser.click(listScreen.listItemAddButton());
        }
        await this.browser.waitForExist(authSocialBlock());
        expect(await this.browser.isVisible(authSocialBlock.providerPrimaryFB())).to.equal(false);
    });
});
