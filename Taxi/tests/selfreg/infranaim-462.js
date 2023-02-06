const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Негатив кнопки "Дальше" страницы personal data без имени', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить поля', () => {
        personalPage.fillForm();
    });

    it('очистить поле Имя', () => {
        personalPage.fldFirstName.click();
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    it('нажать кнопку далее', () => {
        personalPage.goNext();
        assert.isTrue(personalPage.hint.isDisplayed());
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/personal-data');
    });
})