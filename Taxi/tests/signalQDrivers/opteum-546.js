const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: профиль водителя: редактирование: дубликат телефона', () => {
    const alert = 'Номер телефона уже зарегистрирован в системе';

    let newPhone, oldPhone;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Скопировать телефон водителя и перейтии в карточку другого', () => {

        for (let i = 0; i < SignalQDrivers.allRows.length; i++) {
            newPhone = SignalQDrivers.getRow(i + 1).phone.getText();

            if (newPhone) {
                SignalQDrivers.getRow(i + 2).name.click();
                break;
            }
        }

        expect(newPhone).toBeTruthy();
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
