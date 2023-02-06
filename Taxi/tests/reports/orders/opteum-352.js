const ReportsOrders = require('../../../page/ReportsOrders');

describe('Фильтрация по статусу', () => {

    const STATUSES = [
        {name: 'В пути', key: 'driving'},
        {name: 'Ждёт клиента', key: 'waiting'},
        {name: 'Вызов', key: 'calling'},
        {name: 'Везёт клиента', key: 'transporting'},
        {name: 'Выполнен', key: 'complete'},
        {name: 'Отказ', key: 'failed'},
        {name: 'Отменён', key: 'cancelled'},
        {name: 'Истекший', key: 'expired'},
    ];

    it('Открыть страницу отчёт по заказам', () => {
        ReportsOrders.goTo();
    });

    STATUSES.forEach(({name, key}) => {
        describe(name, () => {

            it('Выбрать статус в фильтре', () => {
                ReportsOrders.setDropdownOption(ReportsOrders.filtersList.status, ReportsOrders.statusesList[key]);
            });

            it('Статус отобразился у всех заказов в таблице', () => {
                if (!ReportsOrders.placeholderButton.isExisting()) {
                    expect(ReportsOrders.allRows.status).toHaveTextArrayEachEqual(name);
                }
            });

            it('Удалить статус из фильтра', () => {
                ReportsOrders.multiSelectRemove.click();
            });

        });
    });

});
