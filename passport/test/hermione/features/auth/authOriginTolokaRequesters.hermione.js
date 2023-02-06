const pages = require('../../utils/passportPages');
const PO = require('../../page-objects/auth');

describe('/auth', function() {
    describe('origin = toloka_requesters', function() {
        beforeEach(async function() {
            await this.browser.url(`${pages.AUTH.getUrl()}?origin=toloka_requesters`);
        });
        it('should show social buttons with text', async function() {
            await this.browser.yaShouldHaveVisibleText(PO.authSocialBlock.socialProviderWithText());
        });
    });
});
