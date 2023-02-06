const AutoCard = require('../../../page/AutoCard');
const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

let firstDriverNickName,
    firstDriverTariff;

describe('Переход в карточку водителя', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сохранить данные об автомобиле', () => {
        firstDriverNickName = ReportsQuality.resultTable.firstNickName.getText();
        firstDriverTariff = ReportsQuality.resultTable.firstDriverTariff.getText();
    });

    it('Открыть страницу первого авто', () => {
        ReportsQuality.resultTable.firstNickName.click();
    });

    it('Информация совпадает с данными из таблицы', () => {
        assert.equal(AutoCard.nickNameCell.getValue(), firstDriverNickName);
        assert.include(AutoCard.categoriesBlock.dropdown.getText(), firstDriverTariff);
    });

});
