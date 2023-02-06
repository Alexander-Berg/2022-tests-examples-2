const pages = require('../../../../utils/passportPages');
const {tryDeleteAccountAfterRun} = require('../../../../helpers/api/passport/delete');
const {createNeophonishUser} = require('../../../../helpers/api/passport/registration');
const {processLoginScreen, processPasswordScreen} = require('../screens');
const {processAuthNeophonish} = require('../../processAuthNeophonish');

describe('/auth/complete', function() {
    describe('complete_neophonish', function() {
        it(
            'should show CompleteRegisterPage',
            tryDeleteAccountAfterRun(async function() {
                const user = await createNeophonishUser();

                await processAuthNeophonish(this.browser, user);
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
                await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
            })
        );
        it(
            'should complete registration',
            tryDeleteAccountAfterRun(async function() {
                const user = await createNeophonishUser();

                await processAuthNeophonish(this.browser, user);
                await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
                await processLoginScreen(this.browser);
                await processPasswordScreen(this.browser);
                await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
            })
        );
    });
});
