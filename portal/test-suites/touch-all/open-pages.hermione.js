'use strict';

specs('open-pages', function () {
    it('открывается', async function() {
        await this.browser.yaOpenMorda({
            path: '/all'
        });

        await this.browser.yaHideElement([
            '.services-big__item_text'
        ]);

        await this.browser.yaAssertViewport('index', {
            ignoreElements: [
                '.services-big__item_icon',
                '.services-big__item_link'
            ]
        });
    });
});
