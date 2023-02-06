const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Действие по нажатию на кнопку "Дальше" без Фамилии (негатив)', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    it('очистить поле Фамилия', () => {
        personalPage.fldSecondName.click();
        personalPage.clearWithBackspace(personalPage.fldSecondName);
    });

    it('нажать далее', () => {
        personalPage.goNext();
        assert.equal(personalPage.errorSecondName.getText(), 'Некорректное значение');
    });
});
