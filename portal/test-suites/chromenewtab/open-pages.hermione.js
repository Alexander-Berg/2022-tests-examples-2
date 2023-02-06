'use strict';

specs('open-pages', function () {
    it('tableau', async function() {
        await this.browser.yaOpenMorda({getParams: {content: 'chromenewtab'}});
        await this.browser.$('.informers__item_type_weather').then(elem => elem.waitForDisplayed());
        await this.browser.yaMarkIgnoreElement('.headline__left');
        await this.browser.yaHideElement('.banner');
        await this.browser.yaHideElement('.teaser');

        // промо есть не всегда
        await this.browser.yaHideElement('.main__block-yabrowser-promo');

        // могут быть двухстрочные новости
        await this.browser.yaHideElement('.news__item-content');

        // могут приходить погодные наукасты
        await this.browser.yaHideElement('.desk-notif-card:nth-child(n+2)');

        // ссылка есть не всегда
        await this.browser.yaHideElement('.desk-notif-card_login-plus');

        await this.browser.yaHideElement('.smart-example__sample-link');
        await this.browser.assertView('index', 'html', {
            ignoreElements: [
                '.infinity-zen',
                '.news__header'
            ]
        });
    });
});
