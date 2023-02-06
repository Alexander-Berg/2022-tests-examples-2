import {TicketTypes} from '../types';
import {getPaymentAmount, getTicketTypeByTicket} from '../utils';

const TICKETS = {
    ST_EXTERNAL: 'YANDEXTAXI-15082110',
    ZENDESK: '74395374',
    CHATTERBOX: '5de5e9caeda8a1c11166fbce'
};

describe('utils/getTicketTypeByTicket', () => {
    test('определяем тип тикета как Стартрек', () => {
        const ticketType = getTicketTypeByTicket(TICKETS.ST_EXTERNAL);
        expect(ticketType).toEqual('startrack' as TicketTypes);
    });
    test('определяем тип тикета как Зендеск', () => {
        const ticketType = getTicketTypeByTicket(TICKETS.ZENDESK);
        expect(ticketType).toEqual('zendesk' as TicketTypes);
    });
    test('определяем тип тикета как Чаттербокс', () => {
        const ticketType = getTicketTypeByTicket(TICKETS.CHATTERBOX);
        expect(ticketType).toEqual('chatterbox' as TicketTypes);
    });
});

describe('utils/getPaymentAmount', () => {
    test('корректный подсчет суммы оплаты', () => {
        expect(
            getPaymentAmount({
                ride: 0,
                cashback: 100,
                rebate: 0
            })
        ).toEqual(100);
        expect(
            getPaymentAmount({
                ride: 100,
                cashback: 100,
                rebate: 0
            })
        ).toEqual(200);
        expect(
            getPaymentAmount({
                ride: 1,
                cashback: 0,
                rebate: 100
            })
        ).toEqual(101);
        expect(
            getPaymentAmount({
                ride: 0,
                cashback: 0,
                rebate: 100
            })
        ).toEqual(100);
        expect(
            getPaymentAmount({
                ride: 0,
                cashback: 0,
                rebate: 0
            })
        ).toEqual(0);
        expect(
            getPaymentAmount({
                ride: 0,
                cashback: 0,
                rebate: 0,
                tips: 100
            })
        ).toEqual(0);
        expect(
            getPaymentAmount({
                ride: 200
            })
        ).toEqual(200);
        expect(getPaymentAmount({})).toEqual(undefined);
    });
});
