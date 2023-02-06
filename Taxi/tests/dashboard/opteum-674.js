const DashboardPage = require('../../page/DashboardPage');
const timeouts = require('../../../../utils/consts/timeouts');

describe('Сводка: логирование: подсказки', () => {

    const DATA = {
        hints: [
            ['params.chart_name', 'income'],
            ['params.chart_name', 'orders_sum'],
            ['params.chart_name', 'orders_count'],
            ['params.chart_name', 'active_drivers'],
            ['params.chart_name', 'working_hours'],
        ],
        default: ['action', 'chart_hint_revealed'],
    };

    const metricsPostData = [];

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Запустить перехват запросов метрики', () => {
        DashboardPage.saveMetricsToArray(metricsPostData);
    });

    DATA.hints.forEach((mc, i) => {
        describe(mc.join('='), () => {

            it('Навестись на подсказку чарта', () => {
                DashboardPage.hoverHint(i);
            });

            it('Запросы метрики перехватились', () => {
                browser.pause(timeouts.intercept);
                expect(metricsPostData.length).toBeGreaterThan(0);
            });

            it('Запрос содержит корректные параметры', () => {
                const lastElem = metricsPostData.pop();

                expect(lastElem).toHaveProperty(...DATA.default);
                expect(lastElem).toHaveProperty(...mc);
            });

        });
    });
});
