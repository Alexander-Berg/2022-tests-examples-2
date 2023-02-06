import getDefaultUser from '../getDefaultUser';

const users = [
    {
        id: '1',
        status: {
            value: 'VALID'
        }
    },
    {
        id: '2',
        status: {
            value: 'INVALID'
        }
    }
];

describe('checkAuth', () => {
    describe('getDefaultUser', () => {
        test('it should return null if no arguments was passed', () => {
            expect(getDefaultUser()).toEqual(null);
        });
        test('it should return null if no defaultUid was passed', () => {
            expect(getDefaultUser([])).toEqual(null);
        });
        test('it should return null if wrong types of arguments were passed', () => {
            expect(getDefaultUser(null, 111)).toEqual(null);
            expect(getDefaultUser([], 111)).toEqual(null);
            expect(getDefaultUser(null, '111')).toEqual(null);
        });
        test('it should return null if there was no defaultUser', () => {
            expect(getDefaultUser(users, '111')).toEqual(null);
        });
        test('it should return item with id equal defaultUid', () => {
            expect(getDefaultUser(users, '1')).toEqual({id: '1', status: {value: 'VALID'}});
        });
    });
});
