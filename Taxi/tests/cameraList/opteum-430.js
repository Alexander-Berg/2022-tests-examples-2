const CameraList = require('../../page/signalq/CameraList');
const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Все камеры. Переходы: в раздел "группы камер", в раздел "Все камеры"', () => {

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Нажать на кнопку перехода в раздел групп камер в виде папки"', () => {
        CameraList.groupPageButton.click();
    });

    it('Открылся раздел "Группы камер"', () => {
        DevicesGroups.returnButton.waitForDisplayed();
        expect(DevicesGroups.headerText).toExist();
    });

    it('Нажать кнопку "назад" в виде стрелочки', () => {
        DevicesGroups.returnButton.click();
    });

    it('Открылся раздел "Все камеры"', () => {
        expect(CameraList.headerText).toExist();
    });

});
