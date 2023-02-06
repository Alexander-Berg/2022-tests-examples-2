const DatePicker = require('../../page/DatePicker');
const DriversPage = require('../../page/DriversPage');
const EarningsTab = require('../../page/driverCard/EarningsTab');
const ReportsOrders = require('../../page/ReportsOrders');

describe('Карточка водителя: данные в табе "Заработок" совпадают с данными в разделе "Отчёт по заказам"', () => {

    const DRIVER_ID = 'a33dd7722a8535709cbb2c2988dd96e0';

    let amount, fareInYangoPro, millage, orders;

    it('Открыть раздел "Отчёт по заказам"', () => {
        ReportsOrders.goTo(
            `?driver_id=${DRIVER_ID}`
          + '&order_statuses=complete',
        );
    });

    it('Сохранить данные текущих заказов', () => {
        orders = ReportsOrders.getCells({td: 2}).map(elem => elem.getText());
    });

    it('Выбрать в календаре неделю с предыдущего месяца', () => {
        DatePicker.open();
        DatePicker.scrollToCurrentMonth();
        DatePicker.pickPrevMonth({to: 7});
    });

    it('Данные заказов изменились', () => {
        expect(ReportsOrders.getCells({td: 2})).not.toHaveTextEqual(orders);
    });

    it('Сохранить данные по заказам водителя', () => {
        amount = ReportsOrders.getCells({td: 1}).length;
        fareInYangoPro = ReportsOrders.getFooterRow().fareInYangoPro.getText();
        millage = ReportsOrders.getFooterRow().millage.getText();
    });

    it('Открыть страницу заработка водителя', () => {
        DriversPage.goTo(`/${DRIVER_ID}/income`);
    });

    it('Выбрать в календаре неделю с предыдущего месяца', () => {
        DatePicker.open();
        DatePicker.scrollToCurrentMonth();
        DatePicker.pickPrevMonth({to: 7});
    });

    it('В блоке "Отчет" отображаются соответствующие раннее сохраненным из раздела репортов', () => {
        expect(EarningsTab.report.amount).toHaveTextEqual(String(amount));
        expect(EarningsTab.report.fareInYangoPro).toHaveTextEqual(fareInYangoPro);
        expect(EarningsTab.report.millage).toHaveTextEqual(millage);
    });

});
