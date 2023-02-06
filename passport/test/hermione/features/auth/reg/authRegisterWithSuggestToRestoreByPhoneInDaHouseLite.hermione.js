const pages = require('../../../utils/passportPages');
const PO = require('../../../page-objects/auth/reg');
const preregisterPO = require('../../../page-objects/auth/preregister');

describe('/auth/reg', function() {
    describe('experiment register-with-suggest-to-restore-by-phone-in-da-house-lite', function() {
        beforeEach(async function() {
            await this.browser.url(`${pages.AUTH_REG.getUrl()}?test-id=224000`);
        });
        it('should show PreRegisterPage', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());
            await this.browser.yaShouldBeVisible(preregisterPO.preRegisterPage());
        });
    });
});
