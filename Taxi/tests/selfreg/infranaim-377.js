const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

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
        /* eslint-disable */
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/personal-data');
        /* eslint-enable */
    });
});
