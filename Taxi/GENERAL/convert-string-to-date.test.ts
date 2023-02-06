import moment from 'moment';

import {convertDateStringToDate} from 'server/recognition/date/convert-string-to-date';
import {mapIfNotUndefined} from 'service/utils/map-if-undefined';

describe('convert string to date', () => {
    function runTest(dateString: string, answer: string | undefined) {
        expect(mapIfNotUndefined(convertDateStringToDate(dateString), (date) => date.toString())).toBe(
            mapIfNotUndefined(answer, (date) => moment(date, 'DD-MM-YYYY').utc(true).toDate().toString())
        );
    }

    it('just working', () => {
        runTest('1.2.2021', '01-02-2021');
    });

    it('different splitters', () => {
        runTest('1.2.2021', '01-02-2021');
        runTest('1,2 2021', '01-02-2021');
        runTest('1-2-2021', '01-02-2021');
        runTest('1/2/2021', '01-02-2021');
        runTest('1 2 2021', '01-02-2021');
    });

    it('DD or D, MM or M, YY or YYYY', () => {
        runTest('1.2.2021', '01-02-2021');
        runTest('01.2.2021', '01-02-2021');
        runTest('1.02.2021', '01-02-2021');
        runTest('01.02.2021', '01-02-2021');
        runTest('01.2.21', '01-02-2021');
        runTest('1.2.21', '01-02-2021');
    });

    it('named month', () => {
        runTest('1 янв 2021', '01-01-2021');
        runTest('01 января 2021', '01-01-2021');
        runTest('январь, 1 2021', '01-01-2021');
        runTest('1 февраля 2021', '01-02-2021');
        runTest('2 март, 2021', '02-03-2021');
        runTest('3 апр 2021', '03-04-2021');
        runTest('4 мая 2021', '04-05-2021');
        runTest('5 июн 2021', '05-06-2021');
        runTest('6 июля 2021', '06-07-2021');
        runTest('7 августа 2021', '07-08-2021');
        runTest('8 сент 2021', '08-09-2021');
        runTest('9 октя 2021', '09-10-2021');
        runTest('10 ноября 2021', '10-11-2021');
        runTest('11 дек 2021', '11-12-2021');
    });

    it('not a date', () => {
        runTest('1 2021', undefined);
        runTest('февраль', undefined);
        runTest('31 февраля 2021', undefined);
        runTest(`1.01.${new Date().getFullYear() + 2}`, undefined); // даты в далёком будущем это странно
    });

    it('date in context', () => {
        runTest('Счёт-фактура номер 12345 от 1го апреля 2021г.', '01-04-2021');
        runTest('Счёт-фактура номер 12345/01 от 5 апреля 2021г.', '05-04-2021');
        runTest('12 13 01 2.4.2021 2020', '02-04-2021');
    });
});
