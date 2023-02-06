const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Внутренний"', () => {

    it('Открыть страницу отчёт по заказам 353-4', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Внутренний"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.internal);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Внутренний');
    });
});
