'use strict';

specs('open-pages', function () {
    it('отраница открывается', async function() {
        await this.browser.yaOpenMorda({yaru: true});
        await this.browser.assertView('unauthorized', 'body');
    });
});
