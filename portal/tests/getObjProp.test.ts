import { checkObjProp } from '../getObjProp';

describe('home.checkObjProp', function() {
    test('работает как задумано', function() {
        expect(checkObjProp({ a: 1 }, 'a')).toEqual(true);
        expect(checkObjProp({ a: { a: 1 } }, 'a.a')).toEqual(true);
        expect(checkObjProp({ a: { a: { a: 1 } } }, 'a.a.a')).toEqual(true);
        expect(checkObjProp({}, 'a.a.b')).toEqual(false);
        expect(checkObjProp({ a: { a: { a: 0 } } }, 'a.a.a')).toEqual(false);
        expect(checkObjProp({ a: { a: { a: '0' } } }, 'a.a.a')).toEqual(false);
        expect(checkObjProp({ a: { a: { a: undefined } } }, 'a.a.a')).toEqual(false);
        expect(checkObjProp({ a: { a: { a: 1 } } }, 'a.a.a.a.a.a.a')).toEqual(false);
        expect(checkObjProp({ a: { '': 1 } }, 'a.')).toEqual(true);
    });
});
