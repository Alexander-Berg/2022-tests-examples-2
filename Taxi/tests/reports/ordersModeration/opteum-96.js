const ReportsOrdersModeration = require('../../../page/ReportsOrdersModeration');
const SupportMessagesList = require('../../../page/SupportMessagesList');

describe('Заявка: открытие: на рассмотрении', () => {

    const DATA = {
        status: 'На рассмотрении',
        title: 'Заявка на компенсацию',
        url: `${ReportsOrdersModeration.baseUrl}/support?id=`,
    };

    it('Открыть страницу модерации заказов', () => {
        ReportsOrdersModeration.goTo(
            '?from=2020-01-01T00%3A00'
          + '&to=2023-01-01T00%3A00'
          + '&status=moderation',
        );
    });

    it(`В таблице отобразилась заявка со статусом "${DATA.status}"`, () => {
        expect(ReportsOrdersModeration.getCells({td: 1, tr: 1})).toHaveTextArrayEachEqual(DATA.status, {js: true});
    });

    it('Нажать на первую заявку', () => {
        ReportsOrdersModeration.getCells({td: 1, tr: 1}).click();
    });

    it('Переключиться на открывшийся таб', () => {
        ReportsOrdersModeration.switchTab();
    });

    it('В табе открылась корректная страница', () => {
        expect(browser).toHaveUrlContaining(DATA.url);
    });

    it('В табе отобразился чат', () => {
        expect(SupportMessagesList.supportChatHeaders.title).toHaveTextEqual(DATA.title);
    });

});
