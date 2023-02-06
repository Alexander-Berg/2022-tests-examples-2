const ReportsSummary = require('../../../../page/ReportsSummary');
const TooltipBlock = require('../../../../page/TooltipBlock');

describe('Переход в отчет по заказам', () => {

    const DATA = {
        ordersBetween: [0, 4000],
        tooltip: {
            texts: [
                /^Общее количество заказов: [\d ]+$/,
                /^Общее количество заказов от платформы: [\d ]+$/,
                /^Принято заказов: [\d ]+ \(\d+%\)$/,
                /^Успешно завершены: [\d ]+ \(\d+%\)$/,
                /^Отменён пассажиром: [\d ]+ \(\d+%\)$/,
                /^Отменён водителем: [\d ]+ \(\d+%\)$/,
            ],
            links: [
                {
                    text: 'Список заказов',
                    href: '/reports/orders?date_type=ended_at',
                },
            ],
        },
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/parks');
    });

    it(`В столбце завершенных заказов отображается число между "${DATA.ordersBetween.join(' ... ')}"`, () => {
        expect(ReportsSummary.getCells({td: 6})).toHaveTextNumberBetween(DATA.ordersBetween);
    });

    it('Нажать на завершенные заказы во втором месяце', () => {
        ReportsSummary.getCells({tr: 2, td: 6}).$('span').click();
    });

    it('Отобразился тултип', () => {
        expect(TooltipBlock.texts).toHaveElemVisible();
    });

    DATA.tooltip.texts.forEach((textRe, i) => {
        it(`В строке "${i + 1}" отображается корректный текст "${textRe}"`, () => {
            expect(TooltipBlock.texts[i]).toHaveTextMatch(textRe);
        });
    });

    DATA.tooltip.links.forEach(({text, href}, i) => {
        it(`У ссылки "${i + 1}" отображается корректный текст "${text}"`, () => {
            expect(TooltipBlock.links[i]).toHaveTextEqual(text);
        });

        it(`У ссылки "${i + 1}" отображается корректная ссылка "${href}"`, () => {
            expect(TooltipBlock.links[i]).toHaveAttributeStartsWith('href', href);
        });
    });

    it(`Нажать на ссылку "${DATA.tooltip.links[0].text}"`, () => {
        TooltipBlock.links[0].click();
    });

    it(`Открылась страница "${DATA.tooltip.links[0].href}"`, () => {
        ReportsSummary.switchTab();
        expect(browser).toHaveUrlContaining(ReportsSummary.baseUrl + DATA.tooltip.links[0].href);
    });

});
