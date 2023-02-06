const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: Поиск по ВУ', () => {
    let license;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('отобразить колонку ВУ', () => {
        SignalQDrivers.columnsSelector.click();
        $('button*=ВУ').click();
    });

    it('Ввести в строку поиска ВУ тестового водителя', () => {
        license = SignalQDrivers.getRow().license.getText();
        SignalQDrivers.searchInput.click();
        SignalQDrivers.searchInput.addValue(license);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В таблице отобразились только водители с таким ВУ', () => {
        for (let i = 0; i < SignalQDrivers.allRows.length; i++) {
            expect(SignalQDrivers.getRow(i + 1).license).toHaveTextEqual(license);
        }
    });

});
