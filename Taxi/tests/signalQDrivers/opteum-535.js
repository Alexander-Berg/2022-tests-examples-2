const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: Создание водителя: негатив: дублирующий телефон', () => {
    let phone;
    const hint = 'Номер телефона уже зарегистрирован в системе';
    const name = 'opt535';

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Скопировать телефон другого водителя', () => {

        for (let i = 0; i < SignalQDrivers.allRows.length; i++) {
            phone = SignalQDrivers.getRow(i + 1).phone.getText();

            if (phone) {
                break;
            }
        }

        expect(phone).toBeTruthy();
    });

    it('Нажать на кнопку в виде "+" возле заголовка "Водители"', () => {
        SignalQDrivers.addDriverButton.click();
    });

    it('Заполнить обязательные поля', () => {
        SignalQDrivers.addDriver.doneButton.waitForDisplayed();
        SignalQDrivers.addDriver.lastName.click();
        SignalQDrivers.addDriver.lastName.addValue(name);
        SignalQDrivers.addDriver.lastName.click();
        SignalQDrivers.addDriver.firstName.addValue(name);
        SignalQDrivers.addDriver.phone.click();
        SignalQDrivers.addDriver.phone.addValue(phone);
    });

    it('Нажать кнопку "Готово"', () => {
        SignalQDrivers.addDriver.doneButton.click();
    });

    it('Под полем телефон появился хинт', () => {
        expect(SignalQDrivers.getHint(6)).toHaveTextEqual(hint);
    });

});
