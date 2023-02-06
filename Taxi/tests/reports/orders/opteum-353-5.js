const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Другое"', () => {

    it('Открыть страницу отчёт по заказам 353-5', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Другое"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.other);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('');
    });
});
