const DevicesGroups = require('../../page/signalq/DevicesGroups');

describe('SignalQ. Группы камер. создание группы (негатив)', () => {

    it('открыт раздел "Все камеры"', () => {
        DevicesGroups.goTo();
    });

    it('Нажать на кнопку в виде трёх точек около списка "группы"', () => {
        DevicesGroups.groupDropdownButton.click();
    });

    it('Нажать кнопку "добавить группу"', () => {
        DevicesGroups.addGroupButton.click();
    });

    it('Кнопка готово неактивна', () => {
        DevicesGroups.textInput.waitForDisplayed();
        expect(DevicesGroups.ConfirmButton).toHaveAttribute('disabled');
    });
});
