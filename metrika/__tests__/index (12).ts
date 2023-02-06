import { isNumber, isString } from 'lodash';

import { validateObj } from '..';

test('validateObj', () => {
    const validation = validateObj({
        a: ({ a }) => (isString(a) ? false : { data: true }),
        b: ({ b }) => !isNumber(b),
    });
    expect(validation({ a: 'lol', b: 123 })).toEqual({});
    expect(validation({})).toEqual({ a: { data: true }, b: {} });
});
