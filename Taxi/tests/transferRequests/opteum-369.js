const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

let driverName;

describe('Поиск заявок по водителю', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('В фильтр "Водитель" ввести ФИО любого водителя, который присутствует в списке', () => {
        driverName = TransferRequests.getColumn(1)[0].getText();
        TransferRequests.filters.searchDriverInput.setValue(driverName);
        browser.pause(2000);
    });

    it('отобразились записи только по этому водителю', () => {
        TransferRequests.getColumn(1)[0].waitForDisplayed();
        expect(TransferRequests.getColumn(1)).toHaveTextArrayEachEqual(driverName);
    });

    it('Очистить фильтр', () => {
        TransferRequests.filters.searchDriverInputClearBtn.click();
        browser.pause(2000);
        TransferRequests.getColumn(1)[0].waitForDisplayed();
    });

    it('отобразились записи всех водителей', () => {
        const drivers = TransferRequests.getColumn(1)
            .map(elem => elem.getText())
            .filter(elem => elem !== driverName);

        expect(drivers.length).toBeGreaterThan(0);
    });
});
