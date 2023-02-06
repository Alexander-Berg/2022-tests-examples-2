const ReportsOrdersModeration = require('../../../page/ReportsOrdersModeration');

describe('Фильтрация: по ID заказа', () => {

    const DATA = {
        // номер и id одного и того же заказа
        orders: [
            '321259',
            'cacf24a6a03ddc07abf5b55ce0cab29b',
        ],
    };

    it('Открыть страницу модерации заказов', () => {
        ReportsOrdersModeration.goTo('?from=2022-01-01T17%3A49&to=2022-03-31T15%3A31');
    });

    DATA.orders.forEach((order, i) => {

        describe(order, () => {
            // перед первым вводом чистить не надо
            i > 0 && it('Очистить поиск по ID заказа', () => {
                ReportsOrdersModeration.ordersFilter.erase.click();
            });

            it(`Ввести в поиск по ID заказа "${order}"`, () => {
                ReportsOrdersModeration.queryFilter(ReportsOrdersModeration.ordersFilter, order);
            });

            it('В таблице отобразился корректный заказ', () => {
                expect(ReportsOrdersModeration.getCells({td: 2})).toHaveTextEqual(DATA.orders[0], {js: true});
            });
        });

    });

});
