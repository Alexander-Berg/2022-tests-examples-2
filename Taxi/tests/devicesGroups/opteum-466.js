const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Удаление подгруппы (отмена)', () => {
    const name = 'opteum466';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        DevicesGroups.addSubGroup(name);
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);
    });

    it('Нажать на подгруппу', () => {
        DevicesGroups.getSubGroupByName(name).click();
    });

    it('Нажать на кнопку в виде трёх точек около списка "подгруппы"', () => {
        DevicesGroups.subGroupDropdownButton.click();
    });

    it('Нажать кнопку "Удалить"', () => {
        DevicesGroups.deleteButton.click();
    });

    it('Нажать кнопку "нет"', () => {
        DevicesGroups.declineDeleteButton.click();
    });

    it('Подгруппа НЕ удалена', () => {
        DevicesGroups.goTo();

        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        expect(DevicesGroups.getSubGroupByName(name)).toHaveTextEqual(name);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
