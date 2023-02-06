const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /personal-data (только обязательные поля)', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить обязательные поля в форме', () => {
        personalPage.fillContactEmail('haha@go.brrrr');
        personalPage.fillDateBirth('11.09.2001');
        personalPage.fillFirstName('Калибан');
        personalPage.fillSecondName('Клегг');
    });

    it('форма содержит правильные данные', () => {
        assert.equal(personalPage.fldDateBirth.getValue(), '11.09.2001');
        assert.equal(personalPage.fldFirstName.getValue(), 'Калибан');
        assert.equal(personalPage.fldSecondName.getValue(), 'Клегг');
        assert.equal(personalPage.fldContactEmail.getValue(), 'haha@go.brrrr');
    });
});
