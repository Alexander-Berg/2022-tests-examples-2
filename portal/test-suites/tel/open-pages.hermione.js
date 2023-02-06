'use strict';

specs('open-pages', function () {
    it('index', async function() {
        await this.browser.yaOpenMorda();
        await this.browser.assertView('index', 'form');
    });
});

