const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: Поиск по ФИО', () => {
    let name;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Ввести в строку поиска ФИО тестового водителя', () => {
        name = SignalQDrivers.getRow().name.getText();
        SignalQDrivers.searchInput.click();
        SignalQDrivers.searchInput.addValue(name);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В таблице отобразились только водители с таким ФИО', () => {
        for (let i = 0; i < SignalQDrivers.allRows.length; i++) {
            expect(SignalQDrivers.getRow(i + 1).name).toHaveTextEqual(name);
        }
    });

});
