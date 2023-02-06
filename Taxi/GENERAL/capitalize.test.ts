import {CapitalizeObject, capitalizeObject} from 'service/utils/object/object-keys-transformations/capitalize-object';
import {
    UncapitalizeObject,
    uncapitalizeObject
} from 'service/utils/object/object-keys-transformations/uncapitalize-object';

describe('capitalizeObject', () => {
    it('just works', () => {
        const object = {
            a: 123,
            b: '123',
            c: true,
            D: false,
            [Symbol(213)]: 123
        } as const;

        const capitalizedObject = capitalizeObject(object);

        expect(capitalizedObject).toEqual<CapitalizeObject<typeof object>>({
            A: 123,
            B: '123',
            C: true,
            D: false
        });

        const uncapitalizedObject = uncapitalizeObject(object);

        expect(uncapitalizedObject).toEqual<UncapitalizeObject<typeof object>>({
            a: 123,
            b: '123',
            c: true,
            d: false
        });
    });
});
