const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по типу оплаты "Корп.счёт"', () => {

    it('Открыть страницу отчёт по заказам 353-6', () => {
        ReportsOrders.goTo();
    });

    it('В фильтре "Тип оплаты" выбрать статус "Корп.счёт"', () => {
        ReportsOrders.setDropdownOption(ReportsOrders.filtersList.paymentType, ReportsOrders.paymentTypesList.corp);
    });

    it('Проверить все заказы на соответствие статусу', () => {
        ReportsOrders.checkAllOrdersOnPaymentType('Корп. счёт');
    });
});
