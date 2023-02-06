'use strict';

specs('stocks', function () {
    it('Котировки', async function() {
        await this.browser.yaOpenMorda({getParams: {gramps: 1}});
        await this.browser.$('.inline-stocks__more').then(elem => elem.click());
        await this.browser.$('.inline-stocks__table-title').then(elem => elem.waitForDisplayed());
        await this.browser.yaHideElement('.inline-stocks__table');
        await this.browser.assertView('popup', '.popup_visibility_visible .popup__content');
    });
});
