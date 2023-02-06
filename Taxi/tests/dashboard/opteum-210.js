const DashboardPage = require('../../page/DashboardPage');

describe('Сводка: графики', () => {

    const DATA = {
        graphs: [
            'Доход таксопарка',
            'Сумма по поездкам',
            'Количество заказов',
            'Активные водители',
            'Часы работы',
            'Вы сертифицированы до 22.08.2208',
        ],
    };

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Отображаются корректные заголовки графиков', () => {
        expect(DashboardPage.dashboards.headers).toHaveTextEqual(DATA.graphs, {timeout: 'long'});
    });

    it('В графиках отображаются данные', () => {
        expect(DashboardPage.dashboards.bodies).toHaveElemVisible();
    });

});
