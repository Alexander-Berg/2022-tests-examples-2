const OrderPage = require('../../../page/OrderPage');
const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Предоплата"', () => {

    const DATA = {
        type: 'Платформа',
        url: '/orders',
    };

    let elemsBeforeFilter;

    it('Открыть страницу отчёта по заказам', () => {
        ReportsOrders.goTo();
    });

    it('Отображается список заказов', () => {
        elemsBeforeFilter = ReportsOrders.getCells({td: 2});
        expect(elemsBeforeFilter).toHaveElemLengthAbove(0);
    });

    it('В фильтре "Тип заказа" выбрать статус "Платформа"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.orderType, ReportsOrders.orderTypesList.platform);
    });

    it('Список заказов изменился', () => {
        expect(ReportsOrders.getCells({td: 2})).not.toHaveElemEqual(elemsBeforeFilter);
    });

    it('Открыть последний заказ', () => {
        ReportsOrders.getCells({td: 2}).pop().$('a').click();
    });

    it('Переключиться на открывшийся таб', () => {
        ReportsOrders.switchTab();
    });

    it('В табе открылась корректная страница', () => {
        expect(browser).toHaveUrlContaining(ReportsOrders.baseUrl + DATA.url);
    });

    it('В заказе отображается корректный тип оплаты', () => {
        expect(OrderPage.orderType).toHaveTextEqual(DATA.type);
    });

});
