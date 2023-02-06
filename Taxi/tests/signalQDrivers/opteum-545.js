const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: профиль водителя: редактирование: неверный формат телефона', () => {
    const alert = 'Неверный формат номера телефона';
    let oldPhone;
    const newPhone = '00000';

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на любого водителя в таблице', () => {
        SignalQDrivers.getRow().name.click();
    });

    it(`В поле телефон ввести ${newPhone}`, () => {
        SignalQDrivers.switchTab();
        SignalQDriverCard.driverFullName.waitForDisplayed();
        oldPhone = SignalQDriverCard.phone.getText();
        SignalQDriverCard.phone.click();
        SignalQDriverCard.clearWithBackspace(SignalQDriverCard.focusedInput);
        SignalQDriverCard.focusedInput.addValue(newPhone);
    });

    it('Подтвердить изменение', () => {
        browser.keys('Enter');
    });

    it(`Появился алерт ${alert}`, () => {
        SignalQDriverCard.alert.waitForDisplayed();
        expect(SignalQDriverCard.alert).toHaveTextEqual(alert);
    });

    it('В поле Телефон отображается старое значение ', () => {
        expect(SignalQDriverCard.phone).toHaveTextEqual(oldPhone);
    });

});
