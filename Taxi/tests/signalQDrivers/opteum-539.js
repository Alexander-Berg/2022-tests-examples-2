const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');
const {randomNumLength} = require('../../../../utils/number.js');

describe('SignalQ: водители: Создание водителя', () => {
    const name = `539opt${randomNumLength(10)}`;
    const hiredDate = '01.01.2021';

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
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
    });

    it('Нажать кнопку "Готово"', () => {
        SignalQDrivers.addDriver.doneButton.click();
    });

    it('Открылась карточка водителя', () => {
        SignalQDriverCard.driverFullName.waitForDisplayed();
    });

    it('Данные совпадают с введёными', () => {
        expect(SignalQDriverCard.lastName).toHaveTextEqual(name);
        expect(SignalQDriverCard.firstName).toHaveTextEqual(name);
    });

    it(`Дата приёма на работу ${hiredDate}`, () => {
        expect(SignalQDriverCard.dateHired).toHaveTextEqual(hiredDate);
    });
});
