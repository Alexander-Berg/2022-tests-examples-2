const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание подгруппы (негатив)', () => {
    const name = 'opteum487';

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Подготовка тестовых данных', () => {
        DevicesGroups.clearOldTestData(name);
        DevicesGroups.addGroup(name);
        DevicesGroups.getGroupByName(name).click();
        browser.pause(300);
    });

    it('Нажать на кнопку в виде трёх точек около списка "подгруппы"', () => {
        DevicesGroups.subGroupDropdownButton.click();
    });

    it('Нажать кнопку "добавить подгруппу"', () => {
        DevicesGroups.addSubGroupButton.click();
    });

    it('Кнопка готово неактивна', () => {
        DevicesGroups.textInput.waitForDisplayed();
        expect(DevicesGroups.ConfirmButton).toHaveAttribute('disabled');
    });

    it('Почистить данные', () => {
        DevicesGroups.deleteGroupByName(name);
    });
});
