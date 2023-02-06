const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Удаление подгруппы', () => {
    const name = 'opteum451';

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

    it('Подтвердить удаление', () => {
        DevicesGroups.confirmDeleteButton.click();
    });

    it('Подгруппа удалена', () => {
        DevicesGroups.goTo();

        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        expect(DevicesGroups.emptyGroupText).toHaveTextEqual('Пока нет ни одной подгруппы');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
