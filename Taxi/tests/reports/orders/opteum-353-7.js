const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Предоплата"', () => {

    it('Открыть страницу отчёт по заказам 353-7', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Предоплата"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.prepaid);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Предоплата');
    });
});
