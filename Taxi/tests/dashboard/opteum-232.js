const DashboardPage = require('../../page/DashboardPage');

describe('Сводка: тултипы', () => {

    const DATA = {
        hints: [
            'Виды комиссий таксопарка, которые удерживаются с водителя при работе с платформой. Измеряются в валюте региона каждого аккаунта',
            'Суммы транзакций по заказам, сгруппированные по способу оплаты',
            'Число заказов с группировкой по тарифу, статусу и типу оплаты',
            'Число уникальных водителей, у которых есть заказы в статусах «Выполнен», «Отказ», «Отменён», за этот период',
            'Сумма часов в статусах «Свободный» и «Выполняет заказ» по всем водителям парка',
        ],
    };

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it(`Отображаются "${DATA.hints.length}" кнопок подсказок`, () => {
        expect(DashboardPage.dashboards.hint.buttons).toHaveElemLengthEqual(DATA.hints.length);
    });

    DATA.hints.forEach((elem, i) => {
        it(`При наведении на кнопку подсказки у "${i + 1}" графика отображается корректный текст тултипа`, () => {
            DashboardPage.hoverHint(i);
            expect(DashboardPage.dashboards.hint.tooltips).toHaveTextArrayIncludes(elem);
        });
    });

});
