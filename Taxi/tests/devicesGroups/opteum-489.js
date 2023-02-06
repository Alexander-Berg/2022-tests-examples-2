const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. Переименование подгруппы (негатив)', () => {
    const name = 'opteum489';

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
        browser.pause(300);
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

    it('Кнопка готово неактивна', () => {
        DevicesGroups.textInput.waitForDisplayed();
        expect(DevicesGroups.ConfirmButton).toHaveAttribute('disabled');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
