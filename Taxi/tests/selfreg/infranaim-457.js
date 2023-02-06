const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Действие по нажатию на кнопку "Дальше" без E-mail (негатив)', () => {
    it('пройти до стрницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    it('очистить поле Email', () => {
        personalPage.fldContactEmail.click();
        personalPage.clearWithBackspace(personalPage.fldContactEmail);
    });

    it('нажать далее', () => {
        personalPage.goNext();
        assert.equal(personalPage.errorEmail.getText(), 'Заполните значение');
    });
});
