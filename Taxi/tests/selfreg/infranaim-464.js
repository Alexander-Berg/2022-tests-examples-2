const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Негатив кнопки "Дальше" страницы personal data без даты рождения', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить поля', () => {
        personalPage.fillFirstName('Васян');
        personalPage.fillSecondName('Кашпировский');
        personalPage.fillContactEmail('ka.va@fkf.ru');
    });

    it('нажать кнопку далее', () => {
        personalPage.goNext();
        assert.isTrue(personalPage.hint.isDisplayed());
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/personal-data');
    });
});
