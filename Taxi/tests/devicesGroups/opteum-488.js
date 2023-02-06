const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Переименование группы (негатив)', () => {
    const name = 'opteum488';

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

    it('Кнопка готово неактивна', () => {
        DevicesGroups.textInput.waitForDisplayed();
        expect(DevicesGroups.ConfirmButton).toHaveAttribute('disabled');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
