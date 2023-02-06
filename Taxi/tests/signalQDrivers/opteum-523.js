const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: переход в карточку водителя', () => {
    let name, phone;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на имя водителя в таблице', () => {
        name = SignalQDrivers.getRow().name.getText();
        phone = SignalQDrivers.getRow().phone.getText();

        SignalQDrivers.getRow().name.click();
    });

    it('Данные в карточке водителя соответствуют данным в таблице', () => {
        SignalQDrivers.switchTab();
        SignalQDriverCard.driverFullName.waitForDisplayed();
        expect(name).toContain(SignalQDriverCard.lastName.getText());
        expect(name).toContain(SignalQDriverCard.firstName.getText());

        if (SignalQDriverCard.middleName.getText()) {
            expect(name).toContain(SignalQDriverCard.middleName.getText());
        }

        expect(SignalQDriverCard.phone).toHaveTextEqual(phone);
    });

});
