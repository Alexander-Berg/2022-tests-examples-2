const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Переименование подгруппы', () => {
    const name = 'opteum449';
    const newName = '449opt';

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

    it('Нажать на кнопку в виде трёх точек около списка "Подгруппы"', () => {
        DevicesGroups.subGroupDropdownButton.click();
    });

    it('Нажать кнопку "редактировать"', () => {
        DevicesGroups.editButton.click();
    });

    it('Ввести новое название', () => {
        DevicesGroups.textInput.click();
        DevicesGroups.clearWithBackspace(DevicesGroups.textInput);
        DevicesGroups.textInput.addValue(newName);
    });

    it('Нажать кнопку "готово"', () => {
        DevicesGroups.ConfirmButton.click();
    });

    it('Подгруппа переименована', () => {
        DevicesGroups.goTo();

        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        expect(DevicesGroups.getSubGroupByName(newName)).toHaveTextEqual(newName);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });

});
