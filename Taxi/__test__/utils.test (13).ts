import {prepareWorkingHours} from '../utils';

const TIMETABLES: Indexed = [
    {
        day_type: 'Everyday',
        working_hours: {
            from: {hour: 7, minute: 0},
            to: {hour: 0, minute: 0}
        }
    },
    {
        day_type: 'Weekday',
        working_hours: {
            to: {hour: 17, minute: 0}
        }
    },
    {
        day_type: 'Sunday',
        working_hours: {
            from: {hour: 11, minute: 30}
        }
    }
];

describe('Верный формат workingHours от prepareWorkingHours', () => {
    test('при присутствии from и to', () => {
        const workingHours = prepareWorkingHours(TIMETABLES[0]?.working_hours);
        expect(workingHours).toEqual('7:00 - 0:00');
    });
    test('при присутствии to, но без from', () => {
        const workingHours = prepareWorkingHours(TIMETABLES[1]?.working_hours);
        expect(workingHours).toEqual('до 17:00');
    });
    test('при присутствии from, но без to', () => {
        const workingHours = prepareWorkingHours(TIMETABLES[2]?.working_hours);
        expect(workingHours).toEqual('с 11:30');
    });
});
