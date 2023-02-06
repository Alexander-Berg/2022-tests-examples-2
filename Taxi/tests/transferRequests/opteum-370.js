const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

const statuses = [
    'В обработке',
    'Выполнена',
    'Отклонена банком',
    'Все статусы',
];

describe('Сортировка заявок по статусам', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    for (const status of statuses) {
        it(`В фильтре статусов заявок выбрать статус: ${status}`, () => {
            TransferRequests.filters.status.waitForDisplayed();
            TransferRequests.filters.status.click();
            TransferRequests.selectDropdownItem(status);
            browser.pause(1000);
            TransferRequests.getRow(1).waitForDisplayed();
        });

        it(`отобразились записи со статусом: ${status}`, () => {
            const statusesColumn = TransferRequests.getColumn(7)
                .map(elem => elem.getText())
                .filter(elem => elem.includes(status));

            if (status === 'Все статусы') {
                expect(statusesColumn.length).toEqual(0);
            } else if (!TransferRequests.reportTable.notFound.isDisplayed()) {
                expect(statusesColumn.length).toEqual(TransferRequests.getColumn(7).length);
            }
        });
    }
});
