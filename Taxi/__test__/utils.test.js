const {bufferToObject} = require('../utils');
const {ParseBodyError} = require('../errors');

const MOCK_VALID = Buffer.from(JSON.stringify({body: 'asdadsas', auth: '1wsaSA'}), 'utf-8');
const MOCK_INVALID = Buffer.from('asdasdasd', 'utf-8');

describe('from buffer to object', () => {
    test('buffer to object defines as expected', () => {
        const obj = bufferToObject(MOCK_VALID);

        expect(obj.body).toBeDefined();
    });

    test('buffer to object should return a ParseBodyError', () => {
        expect(() => {
            bufferToObject(MOCK_INVALID);
        }).toThrow(ParseBodyError);
    });

    test('buffer to object should return empty object', () => {
        expect(bufferToObject({})).toEqual({});
    });
});
