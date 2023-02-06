const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель с купленной историей: отчёт', () => {

    const DATA = {
        report: {
            header: 'Отчёт за 28 июл. 2021 г.\n(Данные устарели)',
            blocks: {
                history: 'История BMW X6 Y009YY99\nза последние 5 дней',
                driving: 'Вождение\nРассчитывается алгоритмами Яндекс.Такси',
                activity: 'Активность в сервисе',
                quality: 'Качество',
                reviews: 'Топ отзывов\nКоличество отзывов\nпо сравнению с другими водителями',
            },
            update: 'Обновить за 60 ₽',
        },
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo('?license=5555555555');
    });

    it('Отображается заголовок отчёта', () => {
        expect(ScoringPage.report.header).toHaveTextEqual(DATA.report.header);
    });

    it('Отображаются корректные блоки отчёта', () => {
        expect(ScoringPage.report.titles).toHaveTextEqual(Object.values(DATA.report.blocks));
    });

    it('Отображается кнопка обновления отчёта', () => {
        expect(ScoringPage.report.update).toHaveTextEqual(DATA.report.update);
    });

    Object.keys(DATA.report.blocks).forEach(block => {
        it(`Отображаются данные в блоке "${block}"`, () => {
            expect(ScoringPage.report[block]).toHaveTextOk();
        });
    });

    it('Отображается график активности', () => {
        expect(ScoringPage.report.graph).toHaveElemVisible();
    });

});
