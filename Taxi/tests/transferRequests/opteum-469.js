const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

const driverName = '1111212';

describe('Поиск заявок по водителю (негатив)', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('В фильтр "Водитель" ввести ФИО любого водителя, которого нет в списке', () => {
        TransferRequests.filters.searchDriverInput.setValue(driverName);
        browser.pause(2000);
    });

    it('отобразилась заглушка "Пока ничего нет"', () => {
        expect(TransferRequests.reportTable.notFound).toBeDisplayed();
        expect(TransferRequests.reportTable.notFound).toHaveText('Пока ничего нет');
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
