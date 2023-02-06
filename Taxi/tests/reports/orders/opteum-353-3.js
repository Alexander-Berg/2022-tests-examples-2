const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Карта"', () => {

    it('Открыть страницу отчёт по заказам 353-3', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Карта"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.card);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Карта');
    });
});
