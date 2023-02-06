const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание подгруппы', () => {
    const name = 'opteum447';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Нажать на существующую группу без подгрупп', () => {
        DevicesGroups.getGroupByName(name).click();
    });

    it('Нажать на кнопку в виде трёх точек около списка "подгруппы"', () => {
        DevicesGroups.subGroupDropdownButton.click();
    });

    it('Нажать кнопку "добавить подгруппу"', () => {
        DevicesGroups.addSubGroupButton.click();
    });

    it('Ввести любое название которого нет в списке', () => {
        DevicesGroups.textInput.click();
        DevicesGroups.textInput.addValue(name);
    });

    it('Нажать кнопку "готово"', () => {
        DevicesGroups.ConfirmButton.click();
    });

    it('Подруппа создалась', () => {
        DevicesGroups.goTo();
        DevicesGroups.getGroupByName(name).click();

        browser.pause(500);
        expect(DevicesGroups.getSubGroupByName(name)).toHaveTextEqual(name);
    });

    it('Появилась подгруппа "Все остальные"', () => {
        expect(DevicesGroups.getSubGroupByName('Все остальные')).toHaveTextEqual('Все остальные');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
