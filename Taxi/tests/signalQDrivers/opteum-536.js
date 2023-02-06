const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: Создание водителя: обязательные поля', () => {
    const hint = 'Это поле необходимо заполнить';

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на кнопку в виде "+" возле заголовка "Водители"', () => {
        SignalQDrivers.addDriverButton.click();
    });

    it('Нажать кнопку "готово"', () => {
        SignalQDrivers.addDriver.doneButton.click();
    });

    it(`Под полями имя и фамилия появились хинты ${hint}`, () => {
        expect(SignalQDrivers.getHint(1)).toHaveTextEqual(hint);
        expect(SignalQDrivers.getHint(2)).toHaveTextEqual(hint);
    });
});
