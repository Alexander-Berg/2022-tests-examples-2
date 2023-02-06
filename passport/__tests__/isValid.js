import isValid from '../isValid';

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

const validSessionInfo = {
    status: {
        value: 'VALID'
    },
    default_uid: '1',
    users: users
};

const invalidSessionInfo = {
    status: {
        value: 'INVALID'
    },
    default_uid: '2',
    users: users
};

describe('checkAuth', () => {
    describe('isValid', () => {
        test('it should return true if sessionInfo is valid', () => {
            expect(isValid(validSessionInfo)).toBe(true);
        });

        test('it should return false if sessionInfo is not defined', () => {
            expect(isValid()).toBe(false);
        });

        test('it should return false if sessionInfo is null', () => {
            expect(isValid()).toBe(false);
        });

        test('it should return false if sessionInfo is invalid', () => {
            expect(isValid(invalidSessionInfo)).toBe(false);
        });
    });
});
