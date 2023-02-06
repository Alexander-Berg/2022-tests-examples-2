const DriverCard = require('../../page/driverCard/DriverCard');
const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

describe('Переход в карточку водителя', () => {

    let driverName;

    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('Нажать на ФИО любого водителя в колонке "Водитель"', () => {
        driverName = TransferRequests.getColumn(1)[0].getText();
        TransferRequests.getColumn(1)[0].click();
        TransferRequests.switchTab();
    });

    it('открылась карточка водителя', () => {
        expect(browser).toHaveUrlContaining('/drivers');
    });

    it('данные в карточке совпадают с данными в разделе "Заявки на перевод средств"', () => {
        DriverCard.waitingLoadThisPage(15_000);
        expect(DriverCard.driverNameAndSoname).toHaveTextEqual(driverName);
    });
});
