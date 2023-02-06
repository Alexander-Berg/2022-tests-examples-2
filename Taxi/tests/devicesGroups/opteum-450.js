const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. удаление группы', () => {
    const name = 'opteum450';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Удалить группу', () => {
        DevicesGroups.deleteGroupByName(name);
    });

    it('группа удалена', () => {
        DevicesGroups.goTo();

        DevicesGroups.groupList.forEach(el => {
            expect(el).not.toHaveTextEqual(name);
        });
    });

});
