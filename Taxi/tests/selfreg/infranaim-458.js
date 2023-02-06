const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Действие по нажатию на кнопку "Дальше" без "Дата рождения" (негатив)', () => {
    it('пройти до стрницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить обязательные поля, оставив email пустым', () => {
        personalPage.fillContactEmail('e.kfffff@ail.com');
        personalPage.fillFirstName('вася');
        personalPage.fillSecondName('петя');
    });

    it('нажать далее', () => {
        personalPage.goNext();
        personalPage.errorDateBirth.waitForDisplayed();
        assert.equal(personalPage.errorDateBirth.getText(), 'Заполните значение');
    });
});
