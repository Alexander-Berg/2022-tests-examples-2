const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Нельзя удалить подгруппу "Все остальные"', () => {
    const name = 'opteum472';
    const subGroup = 'Все остальные';

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
        DevicesGroups.getSubGroupByName(subGroup).click();
    });

    it('Нажать на кнопку в виде трёх точек около списка "подгруппы"', () => {
        DevicesGroups.subGroupDropdownButton.click();
    });

    it('Нажать кнопку "Удалить"', () => {
        DevicesGroups.deleteButton.click();
    });

    it('Подтвердить удаление', () => {
        DevicesGroups.confirmDeleteButton.click();
    });

    it('Подгруппа НЕ удалена', () => {
        DevicesGroups.goTo();

        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        expect(DevicesGroups.getSubGroupByName(subGroup)).toHaveTextEqual(subGroup);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
