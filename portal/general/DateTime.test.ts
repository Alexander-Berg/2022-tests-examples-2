import { getDateTime } from './DateTime';

describe('DateTime#getDateTime()', () => {
    const currentDate = new Date(2020, 11, 15, 12, 30);

    it('Должна формировать правильную короткую дату', () => {
        expect(getDateTime(currentDate, new Date(2020, 11, 15, 12, 26))).toStrictEqual('12:26');
        expect(getDateTime(currentDate, new Date(2020, 11, 15, 12, 25))).toStrictEqual('12:25');
        expect(getDateTime(currentDate, new Date(2020, 11, 15, 11, 30))).toStrictEqual('11:30');
        expect(getDateTime(currentDate, new Date(2020, 11, 15, 7, 31))).toStrictEqual('7:31');

        expect(getDateTime(currentDate, new Date(2020, 11, 15, 7, 30))).toStrictEqual('7:30');
        expect(getDateTime(currentDate, new Date(2020, 11, 15, 0, 0))).toStrictEqual('0:00');

        expect(getDateTime(currentDate, new Date(2020, 11, 14, 23, 59))).toStrictEqual('вчера, 23:59');
        expect(getDateTime(currentDate, new Date(2020, 11, 14, 7, 1))).toStrictEqual('вчера, 7:01');
        expect(getDateTime(currentDate, new Date(2020, 11, 14, 0, 0))).toStrictEqual('вчера, 0:00');

        expect(getDateTime(currentDate, new Date(2020, 11, 13, 23, 59))).toStrictEqual('13 дек, 23:59');
        expect(getDateTime(currentDate, new Date(2020, 11, 1))).toStrictEqual('1 дек, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 10, 10))).toStrictEqual('10 ноя, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 9, 15))).toStrictEqual('15 окт, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 8, 7))).toStrictEqual('7 сен, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 7, 3))).toStrictEqual('3 авг, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 6, 24))).toStrictEqual('24 июл, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 5, 12))).toStrictEqual('12 июн, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 4, 18))).toStrictEqual('18 мая, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 3, 30))).toStrictEqual('30 апр, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 2, 8))).toStrictEqual('8 мар, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 1, 23))).toStrictEqual('23 фев, 0:00');
        expect(getDateTime(currentDate, new Date(2020, 0, 1))).toStrictEqual('1 янв, 0:00');

        expect(getDateTime(currentDate, new Date(2019, 11, 31))).toStrictEqual('31 дек, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 11, 1))).toStrictEqual('1 дек, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 10, 1))).toStrictEqual('1 ноя, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 9, 1))).toStrictEqual('1 окт, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 8, 1))).toStrictEqual('1 сен, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 7, 1))).toStrictEqual('1 авг, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 6, 1))).toStrictEqual('1 июл, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 5, 1))).toStrictEqual('1 июн, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 4, 1))).toStrictEqual('1 мая, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 3, 1))).toStrictEqual('1 апр, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 2, 1))).toStrictEqual('1 мар, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 1, 1))).toStrictEqual('1 фев, 0:00');
        expect(getDateTime(currentDate, new Date(2019, 0, 1))).toStrictEqual('1 янв, 0:00');

        expect(getDateTime(currentDate, new Date(2018, 11, 31))).toStrictEqual('31 дек, 0:00');
    });
});
