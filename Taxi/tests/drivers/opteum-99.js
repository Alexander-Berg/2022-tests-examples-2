const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 30_000;

describe('Карточка водителя: ведомость', () => {
    it('Перейти на страницу отчёта по транзакциям', () => {
        DriversPage.goTo();
        const reportForTransactionUrl = 'https://fleet.tst.yandex.ru/reports/transactions/list?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru';
        browser.url(reportForTransactionUrl);
    });

    it('Перейти на страницу водителя', () => {
        const firstDriverInTable = $('tbody tr:nth-child(1) td:nth-child(2) a');
        firstDriverInTable.waitForDisplayed({timeout: timeToWaitElem});
        firstDriverInTable.click();

        DriverCard.switchTab();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Открыть раздел "Ведомость" в карточке водителя', () => {
        $('span=Ведомость').click();
        const firstRowInTable = $('tbody tr:nth-child(1)');
        firstRowInTable.waitForDisplayed({timeout: timeToWaitElem});
    });
});
