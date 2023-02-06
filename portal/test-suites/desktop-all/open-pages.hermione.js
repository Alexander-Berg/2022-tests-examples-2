'use strict';

specs('open-pages', function () {
    it('открывается', async function() {
        await this.browser.yaOpenMorda({
            path: '/all'
        });

        await this.browser.execute(function () {
            document.documentElement.className += ' font_loaded';
        });

        await this.browser.yaHideElement([
            '.b-line__services-main tr:nth-child(n + 2)',
            '.services-big__item_text',
            '.services-all',
            '.b-line__services-bottom tr:nth-child(n + 2)'
        ]);

        await this.browser.assertView('index', 'body', {
            ignoreElements: [
                '.services-big__item_icon',
                '.services-big__item_link',
                '.footer__link_copy'
            ]
        });
    });
});
