const pages = require('../../../../utils/passportPages');
const PO = require('../../../../page-objects/auth/reg');
const preregisterPO = require('../../../../page-objects/auth/preregister');
const {createAutoregisteredUser} = require('../../../../helpers/api/passport/registration');

describe('/auth/complete', function() {
    describe.skip('complete_autoregistered', function() {
        beforeEach(async function() {
            const user = await createAutoregisteredUser();

            await this.browser.yaAuth(user);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
        });
        it('should show CompleteRegisterPage', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());
            await this.browser.yaShouldBeVisible(preregisterPO.preRegisterPage());
        });
    });
});
