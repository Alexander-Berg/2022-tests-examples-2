const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Действие по нажатию на кнопку "Дальше" без Имени (негатив)', () => {
    it('пройти до стрницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    it('очистить поле Имя', () => {
        personalPage.fldFirstName.click();
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    it('нажать далее', () => {
        personalPage.goNext();
        assert.equal(personalPage.errorFirstName.getText(), 'Некорректное значение');
    });
});
