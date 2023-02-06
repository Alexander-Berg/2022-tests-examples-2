const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Нельзя переименовать подгруппу "Все остальные"', () => {
    const name = 'opteum473';
    const subGroup = 'Все остальные';
    const newName = '473opt';

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

    it('Отобразилась ошибка "Не удалось переименовать подгруппу"', () => {
        expect(DevicesGroups.renameSubGroupErrorAlert).toHaveTextEqual('Не удалось переименовать подгруппу');
    });

    it('Подгруппа НЕ переименована', () => {
        DevicesGroups.goTo();

        DevicesGroups.getGroupByName(name).click();
        browser.pause(500);

        expect(DevicesGroups.getSubGroupByName(subGroup)).toHaveTextEqual(subGroup);
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
