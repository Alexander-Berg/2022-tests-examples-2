const DashboardPage = require('../../page/DashboardPage');
const timeouts = require('../../../../utils/consts/timeouts');

describe('Сводка: логирование: количество заказов', () => {

    const DATA = {
        hints: [
            ['params.chart_name', 'status'],
            ['params.chart_name', 'tariff'],
            ['params.chart_name', 'payment'],
        ],
        default: ['action', 'orders_count_chart_grouping_changed'],
    };

    const metricsPostData = [];

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Запустить перехват запросов метрики', () => {
        DashboardPage.saveMetricsToArray(metricsPostData);
    });

    // первая радиокнопка выбрана по умолчанию
    // поэтому итерируемся в обратную сторону — от последней радиокнопки к первой
    // чтобы нажатие на неё тоже проверить
    for (let i = DATA.hints.length - 1; i >= 0; i--) {
        describe(DATA.hints[i].join('='), () => {

            it('Нажать на радиокнопку в чарте количества заказов', () => {
                DashboardPage.ordersDash.buttons[i].click();
            });

            it('Запросы метрики перехватились', () => {
                browser.pause(timeouts.intercept);
                expect(metricsPostData.length).toBeGreaterThan(0);
            });

            it('Запрос содержит корректные параметры', () => {
                const lastElem = metricsPostData.pop();

                expect(lastElem).toHaveProperty(...DATA.default);
                expect(lastElem).toHaveProperty(...DATA.hints[i]);
            });

        });
    }
});
