const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Переименование группы', () => {
    const name = 'opteum448';
    const newName = '448opt';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
    });

    it('Нажать на группу', () => {
        DevicesGroups.getGroupByName(name).click();
    });

    it('Нажать на кнопку в виде трёх точек около списка "группы"', () => {
        DevicesGroups.groupDropdownButton.click();
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

    it('Группа переименована', () => {
        DevicesGroups.goTo();

        expect(DevicesGroups.getGroupByName(newName)).toHaveTextEqual(newName);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(newName);
    });

});
