const DevicesGroups = require('../../page/signalq/DevicesGroups');
const Statistic = require('../../page/signalq/Statistic');

describe('SignalQ. Статистика. Переходы: в раздел "группы камер", в раздел "Статистика"', () => {

    it('Открыт раздел "Статистика"', () => {
        Statistic.goTo();
    });

    it('Нажать на кнопку перехода в раздел групп камер в виде папки', () => {
        Statistic.groupPageButton.click();
    });

    it('Открылся раздел "Группы камер"', () => {
        DevicesGroups.returnButton.waitForDisplayed();
        expect(DevicesGroups.headerText).toExist();
    });

    it('Нажать кнопку "назад" в виде стрелочки', () => {
        DevicesGroups.returnButton.click();
    });

    it('Открылся раздел "Статистика"', () => {
        expect(Statistic.groupPageButton).toExist();
    });

});
