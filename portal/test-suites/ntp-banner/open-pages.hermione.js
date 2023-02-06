'use strict';

specs('open-pages', function () {
    it('index', async function() {
        await this.browser.yaOpenMorda({
            path: '/portal/ntp/banner/',
            getParams: {
                content: 'yabrotab'
            }
        });
    });
});
