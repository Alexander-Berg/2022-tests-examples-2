const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание группы', () => {
    const name = 'opteum446';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
        DevicesGroups.clearOldTestData(name);
    });

    it('Нажать на кнопку в виде трёх точек около списка "группы"', () => {
        DevicesGroups.groupDropdownButton.click();
    });

    it('Нажать кнопку "добавить группу"', () => {
        DevicesGroups.addGroupButton.click();
    });

    it('Ввести любое название которого нет в списке', () => {
        DevicesGroups.textInput.click();
        DevicesGroups.textInput.addValue(name);
    });

    it('Нажать кнопку "готово"', () => {
        DevicesGroups.ConfirmButton.click();
    });

    it('Группа создалась', () => {
        DevicesGroups.goTo();
        expect(DevicesGroups.getGroupByName(name)).toHaveTextEqual(name);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });

});
