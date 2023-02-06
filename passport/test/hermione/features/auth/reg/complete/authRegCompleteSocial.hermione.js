const pages = require('../../../../utils/passportPages');
const {isProd, isRc} = require('../../../../testEnvironmentConfig');
const {setAuthCookiesByUid} = require('../../setAuthCookiesByUid');

describe('/auth/complete', function() {
    describe('complete_social for default configs', function() {
        it('should start complete', async function() {
            const uid = !(isProd() || isRc()) ? 4090224570 : null; // TODO создать социальщика с портальным алиасом

            if (!uid) {
                return;
            }

            await setAuthCookiesByUid(this.browser, uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
        });
    });
    describe('complete_social for test origin', function() {
        it('should start complete', async function() {
            const uid = !(isProd() || isRc()) ? 4090224570 : null; // TODO создать социальщика с портальным алиасом

            if (!uid) {
                return;
            }

            await setAuthCookiesByUid(this.browser, uid);
            await this.browser.url(`${pages.AUTH_REG_COMPLETE.getUrl()}?origin=test_noPersonalData_regComplete`);
            await this.browser.yaShouldBeAtUrl(pages.AUTH_REG_COMPLETE.getUrl());
        });
    });
});
