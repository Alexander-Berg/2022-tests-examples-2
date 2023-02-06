const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. добавление камеры (негатив)', () => {
    const name = 'opteum490';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);
    });

    it('Нажать на кнопку в виде трёх точек около списка "Камеры"', () => {
        DevicesGroups.cameraDropdownButton.click();
    });

    it('Нажать на кнопку "добавить камеру"', () => {
        DevicesGroups.addCameraButton.click();
        browser.pause(500);
    });

    it('Нажать на кнопку "добавить камеру"', () => {
        DevicesGroups.addCameraSaveButton.waitForDisplayed();
        expect(DevicesGroups.addCameraSaveButton).toHaveAttribute('disabled');
    });

    it('Почистить данные', () => {
        DevicesGroups.goTo();
        DevicesGroups.deleteGroupByName(name);
    });
});
