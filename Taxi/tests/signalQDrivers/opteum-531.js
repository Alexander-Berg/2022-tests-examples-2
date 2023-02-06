const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: Поиск по телефону', () => {
    let phone;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Ввести в строку поиска телефон тестового водителя', () => {
        phone = SignalQDrivers.getRow().phone.getText();
        SignalQDrivers.searchInput.click();
        SignalQDrivers.searchInput.addValue(phone);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В таблице отобразились только водители с таким телефоном', () => {
        for (let i = 0; i < SignalQDrivers.allRows.length; i++) {
            expect(SignalQDrivers.getRow(i + 1).phone).toHaveTextEqual(phone);
        }
    });

});
