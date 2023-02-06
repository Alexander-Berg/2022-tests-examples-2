const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание групп с одинаковыми именами', () => {
    const name = 'opteum484';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
    });

    it('Создать две группы с одинаковыми названиями', () => {
        DevicesGroups.addGroup(name);
        DevicesGroups.addGroup(name);
    });

    it('Добавить в одну из групп подгруппу', () => {
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        DevicesGroups.addSubGroup(name);
    });

    it('Подгруппа отображается только в одной группе', () => {
        DevicesGroups.goTo();
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        expect(DevicesGroups.getSubGroupByName(name)).toHaveTextEqual(name);
        DevicesGroups.deleteGroupByName(name);

        DevicesGroups.goTo();
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
        expect(DevicesGroups.emptyGroupText).toHaveTextEqual('Пока нет ни одной подгруппы');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });

});
