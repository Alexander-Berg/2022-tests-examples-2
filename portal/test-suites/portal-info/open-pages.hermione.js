'use strict';

specs('open-pages', function () {
    it('index', async function() {
        await this.browser.yaOpenMorda({
            path: '/portal/info/dmetro20180921'
        });

        await this.browser.assertView('index', 'html');
    });
});
