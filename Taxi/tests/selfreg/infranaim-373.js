const { assert } = require('chai');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');

describe('Негатив кнопки "Дальше" страницы citizenship', () => {
    it('пройти до страницы /citizenship', () => {
        citizenshipPage.open();
    });

    it('нажать кнопку дальше', () => {
        citizenshipPage.goNext();
        citizenshipPage.hint.waitForDisplayed();
        assert.equal(citizenshipPage.hint.getText(), 'Выберите значение');
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/citizenship');
    });
});
