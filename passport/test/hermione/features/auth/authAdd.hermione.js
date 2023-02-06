const pages = require('../../utils/passportPages');

describe('/auth/add', () => {
    beforeEach(async function() {
        await this.browser.url(pages.AUTH_ADD.getUrl());
    });
    it('should show domik', async function() {
        await this.browser.yaShouldBeVisible(this.PO.auth());
        await this.browser.yaShouldBeVisible(this.PO.auth.loginInput());
    });
});
