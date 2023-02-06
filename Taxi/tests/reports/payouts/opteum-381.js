const ReportsPayouts = require('../../../page/ReportsPayouts');

describe('Выплаты. Открытие платежного поручения', () => {

    const PAYOUT_ID = 512_956;

    const DATA = {
        title: `Выплата ${PAYOUT_ID}`,

        report: [
            `Выплачено ${PAYOUT_ID} 9 мар. 2020 г., 08:10`,
            'some_bank_account_number',
            'Платежка для леща тут какое то описание',
            '40 001,00 ₽',
        ].join('\n'),

        payout: {
            notFound: 'Пока ничего нет',
        },
    };

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo('?date_from=2020-03-09T17%3A13&date_to=2020-03-10T17%3A13');
    });

    it('Отображается корректный текст в первой строке таблицы выплат', () => {
        expect(ReportsPayouts.getCells({tr: 1})).toHaveTextEqual(DATA.report);
    });

    it('Открыть первую выплату', () => {
        ReportsPayouts.getCells({tr: 1, td: 1}).click();
    });

    it('Отображается корректный заголовок', () => {
        expect(ReportsPayouts.payoutBlock.title).toHaveTextEqual(DATA.title);
    });

    it('Отображается текст заглушки', () => {
        expect(ReportsPayouts.reportTable.notFound).toHaveTextEqual(DATA.payout.notFound);
    });

});
