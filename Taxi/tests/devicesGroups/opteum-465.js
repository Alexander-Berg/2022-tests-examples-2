const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. удаление группы (отмена)', () => {
    const name = 'opteum465';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Удалить группу', () => {
        DevicesGroups.getGroupByName(name).click();

    });

    it('Нажать на кнопку в виде трёх точек около списка "группы"', () => {
        DevicesGroups.groupDropdownButton.click();
    });

    it('Нажать кнопку "удалить группу"', () => {
        DevicesGroups.deleteButton.click();
    });

    it('Нажать кнопку "нет"', () => {
        DevicesGroups.declineDeleteButton.click();
    });

    it('Группа НЕ удалена', () => {
        DevicesGroups.goTo();
        expect(DevicesGroups.getGroupByName(name)).toHaveTextEqual(name);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
