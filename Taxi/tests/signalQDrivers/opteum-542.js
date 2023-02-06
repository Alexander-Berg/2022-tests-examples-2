const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: профиль водителя: редактирование: отчистить фамилию', () => {
    const hint = 'Это поле необходимо заполнить';
    let name;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на любого водителя в таблице', () => {
        SignalQDrivers.getRow().name.click();
    });

    it('Отчистить поле фамилии', () => {
        SignalQDrivers.switchTab();
        SignalQDriverCard.driverFullName.waitForDisplayed();
        name = SignalQDriverCard.lastName.getText();
        SignalQDriverCard.lastName.click();
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

    it('В поле Фамилия отображается старое значение ', () => {
        expect(SignalQDriverCard.lastName).toHaveTextEqual(name);
    });

});
