'use strict';

specs('keyboard', function () {
    it('Виртуальная клавиатура', async function() {
        await this.browser.yaOpenMorda({getParams: {gramps: 1}});
        await this.browser.$('.keyboard-loader').then(elem => elem.click());
        await this.browser.$('.keyboard-popup').then(elem => elem.waitForDisplayed());
        await this.browser.assertView('popup', '.keyboard-popup');
    });
});
