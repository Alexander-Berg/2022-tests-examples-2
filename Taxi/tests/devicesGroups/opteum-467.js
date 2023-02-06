const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. добавление камеры в подгруппу (негатив)', () => {
    const name = 'opteum464';

    it('Подготовка тестовых данных', () => {
        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addSubGroup(name);
        browser.pause(300);
    });

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);
    });

    it('Нажать на подгруппу', () => {
        DevicesGroups.getSubGroupByName(name).click();
    });

    it('Нажать на кнопку в виде трёх точек около списка "Камеры"', () => {
        DevicesGroups.cameraDropdownButton.click();
    });

    it('Нажать на кнопку "добавить камеру"', () => {
        DevicesGroups.addCameraButton.click();
        browser.pause(500);
    });

    it('Нажать на кнопку "добавить камеру"', () => {
        expect(DevicesGroups.noCameraSidebarText).toHaveTextEqual('Пока нет ни одной камеры');
    });

    it('Почистить данные', () => {
        DevicesGroups.goTo();
        DevicesGroups.deleteGroupByName(name);
    });
});
