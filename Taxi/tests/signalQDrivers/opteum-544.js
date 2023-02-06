const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: профиль водителя: редактирование: отчистить дату', () => {
    const hint = 'Это поле необходимо заполнить';
    let date;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на любого водителя в таблице', () => {
        SignalQDrivers.getRow().name.click();
    });

    it('Отчистить поле даты найма', () => {
        SignalQDrivers.switchTab();
        SignalQDriverCard.driverFullName.waitForDisplayed();
        date = SignalQDriverCard.dateHired.getText();
        SignalQDriverCard.dateHired.click();
        SignalQDriverCard.clearWithBackspace(SignalQDriverCard.focusedInput);
    });

    it('Подтвердить изменение', () => {
        browser.keys('Enter');
    });

    it(`Появился хинт ${hint}`, () => {
        expect(SignalQDriverCard.hint).toHaveTextEqual(hint);
    });

    it('Обновить страницу', () => {
        browser.refresh();
    });

    it('В поле Даты найма отображается старое значение ', () => {
        expect(SignalQDriverCard.dateHired).toHaveTextEqual(date);
    });

});
