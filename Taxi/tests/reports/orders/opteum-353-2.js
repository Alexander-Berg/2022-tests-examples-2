const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Безналичные"', () => {

    it('Открыть страницу отчёт по заказам 353-2', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Безналичные"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.cashless);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Безналичные');
    });
});
