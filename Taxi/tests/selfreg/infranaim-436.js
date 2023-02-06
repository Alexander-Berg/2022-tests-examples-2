const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();

describe('Выбор страны "Российская Федерация" и города "Москва" /placement', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    it('выбрать Москву в списке городов', () => {
        placementPage.selectCity('Москва');
        assert.equal(placementPage.activeCity.getText(), 'Москва', 'Выбран город не Москва');
    });
});
