import {getInitialStampDateTimeToView, getInitialStampDateToView} from '../utils';

const EXAMPLE_TIME = '23:00';
const EXAMPLE_DATE_ISO = '2019-10-30T18:00:00.000Z';
const EXAMPLE_DATETIME = `2019-10-30T${EXAMPLE_TIME}:00+0000`;
const EXAMPLE_UTC_OFFSET = 300;

describe('utils/getInitialStampDateToView', () => {
    test('проверка верной даты для отображения в форме', () => {
        const dateToView = getInitialStampDateToView(EXAMPLE_DATETIME, EXAMPLE_UTC_OFFSET);
        const timeToView = getInitialStampDateTimeToView(dateToView, EXAMPLE_UTC_OFFSET);
        expect(dateToView).toEqual(EXAMPLE_DATE_ISO);
        expect(timeToView).toEqual(EXAMPLE_TIME);
    });
});
