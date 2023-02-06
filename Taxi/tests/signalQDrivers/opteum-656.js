const SignalQDrivers = require('../../page/signalq/SignalQDrivers');
const {randomNumLength} = require('../../../../utils/number.js');

describe('SignalQ: водители: Создание водителя: негатив: крестик', () => {
    const phone = `7${randomNumLength(10)}`;
    const name = 'opt656';

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
        SignalQDrivers.addDriver.phone.click();
        SignalQDrivers.addDriver.phone.addValue(phone);
    });

    it('Нажать кнопку закрытия карточки в виде "Х"', () => {
        SignalQDrivers.addDriver.closeButton.click();
    });

    it('Пользователь не создан', () => {
        SignalQDrivers.searchInput.click();
        SignalQDrivers.searchInput.addValue(phone);
        browser.keys('Enter');
        browser.pause(1000);
        expect(SignalQDrivers.noDataAvailable).toHaveTextEqual('Тут ничего нет');
        expect(SignalQDrivers.resetFilters).toExist();
    });
});
