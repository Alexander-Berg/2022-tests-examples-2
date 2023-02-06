const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Наличные"', () => {

    it('Открыть страницу отчёт по заказам 353-1', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Наличные"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.cash);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Наличные');
    });
});
