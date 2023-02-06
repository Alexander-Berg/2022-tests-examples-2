const ReportsPayouts = require('../../../page/ReportsPayouts');

describe('Выплаты. Остаток по договорам', () => {

    const DATA = {
        title: 'Выплаты\nSea bream',
        balance: [
            'Доступный остаток по договорам на –',
            '0,00',
            'Автоматическое перечисление запланировано на –',
        ],
        client: {
            id: [
                'ID клиента',
                '100500',
            ],
            account: [
                'Лицевой счёт',
                '0,00 ₽',
                'Пополнить',
            ],
            limit: /^Лимит по лицевому счёту\n-\d{3} \d{3} \d{3},\d{1,2} ₽$/,
            inn: [
                'ИНН',
                '381805387129',
            ],
            payment: [
                'Расчётный счёт',
                '40802810924130000114',
            ],
            bik: [
                'БИК',
                '044525411',
            ],
        },
    };

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo('?date_from=2020-03-09T17%3A13&date_to=2020-03-10T17%3A13');
    });

    it('Отображается корректный заголовок', () => {
        expect(ReportsPayouts.sideBlock.title).toHaveTextEqual(DATA.title);
    });

    it('Отображается корректный баланс', () => {
        expect(ReportsPayouts.sideBlock.balance).toHaveTextEqual(DATA.balance.join('\n'));
    });

    it('Отображается корректный ID клиента', () => {
        expect(ReportsPayouts.sideBlock.client.id).toHaveTextEqual(DATA.client.id.join('\n'));
    });

    it('Отображается корректный лицевой счёт клиента', () => {
        expect(ReportsPayouts.sideBlock.client.account).toHaveTextEqual(DATA.client.account.join('\n'));
    });

    it('Отображается корректный лимит клиента', () => {
        expect(ReportsPayouts.sideBlock.client.limit).toHaveTextMatch(DATA.client.limit);
    });

    it('Отображается корректный ИНН клиента', () => {
        expect(ReportsPayouts.sideBlock.client.inn).toHaveTextEqual(DATA.client.inn.join('\n'));
    });

    it('Отображается корректный РС клиента', () => {
        expect(ReportsPayouts.sideBlock.client.payment).toHaveTextEqual(DATA.client.payment.join('\n'));
    });

    it('Отображается корректный БИК клиента', () => {
        expect(ReportsPayouts.sideBlock.client.bik).toHaveTextEqual(DATA.client.bik.join('\n'));
    });

});
