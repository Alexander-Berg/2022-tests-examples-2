const ReportsOrdersModeration = require('../../../page/ReportsOrdersModeration');

describe('Фильтрация: по статусу заявки', () => {

    const DATA = {
        statuses: [
            {
                name: 'Все',
                index: 0,
                orders: /^(completed|Подать заявку|На рассмотрении)$/,
            },
            {
                name: 'Подать заявку',
                index: 1,
                orders: /^(completed|Подать заявку)$/,
            },
            {
                name: 'На рассмотрении',
                index: 2,
                orders: /^(completed|На рассмотрении)$/,
            },
        ],
    };

    const defaultStatus = DATA.statuses[0].name;

    it('Открыть страницу модерации заказов', () => {
        ReportsOrdersModeration.goTo('?from=2022-01-01T16%3A34&to=2022-03-31T15%3A31');
    });

    it(`Выбран фильтр статуса по умолчанию "${defaultStatus}"`, () => {
        expect(ReportsOrdersModeration.statusFilter.input).toHaveTextEqual(defaultStatus);
    });

    DATA.statuses.reverse().forEach(status => {

        it(`Выбрать фильтр статуса "${status.name}"`, () => {
            ReportsOrdersModeration.statusFilter.input.click();
            ReportsOrdersModeration.selectOption[status.index].click();
        });

        it(`В таблице отобразились заявки со статусом "${status.orders}"`, () => {
            expect(ReportsOrdersModeration.getCells({td: 1})).toHaveTextMatch(status.orders, {js: true});
        });

    });

});
