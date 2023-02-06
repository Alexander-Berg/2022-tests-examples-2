const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /citizenship', () => {
    it('пройти до страницы /placement', () => {
        citizenshipPage.open();
        citizenshipPage.fill();
        citizenshipPage.goNext();
    });

    it('нажать далее', () => {
        personalPage.fldContactEmail.waitForDisplayed();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/personal-data');
    });
});
