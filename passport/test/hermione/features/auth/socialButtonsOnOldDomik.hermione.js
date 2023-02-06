const {expect} = require('chai');
const pages = require('../../utils/passportPages');
const {domik} = require('../../page-objects/auth');

describe('/auth?new=0 socialButtons on old domik', function() {
    it('should show facebook social button with exp: social-provider-fb-exp', async function() {
        await this.browser.url(`${pages.AUTH.getUrl()}?new=0&flag-ids=social-provider-fb-exp`);
        await this.browser.waitForExist(domik());
        await this.browser.waitForExist(domik.social.iconFB());
    });
    it('should hidden facebook social button without exp: social-provider-fb-exp', async function() {
        await this.browser.url(`${pages.AUTH.getUrl()}?new=0`);
        await this.browser.waitForExist(domik());
        expect(await this.browser.isVisible(domik.social.iconFB())).to.equal(false);
    });
});
