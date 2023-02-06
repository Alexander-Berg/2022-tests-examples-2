import putils from 'putils';

describe('merge', () => {
    it.each([
        [[{a: [123]}, {a: null}], {a: null}],
        [[{a: [123]}, {a: {foo: 'bar'}}], {a: {foo: 'bar'}}],
        [[{a: {foo: 'bar'}}, {a: [123]}], {a: [123]}],
        [[{a: []}, {a: 'sdf'}], {a: 'sdf'}],
        [[{a: ['asd', 'qwe']}, {a: [123]}], {a: [123]}],
        [[{a: 'a'}, {b: 'b'}], {a: 'a', b: 'b'}],
        [[{a: 'a'}, {b: 'b'}, {c: 'c'}], {a: 'a', b: 'b', c: 'c'}],
        [[{}, {a: {aa: 'aa'}}], {a: {aa: 'aa'}}],
        [[{b: 'b'}, {a: {aa: 'aa'}}], {a: {aa: 'aa'}, b: 'b'}],
        [[{b: {bb: 'bb'}}, {a: {aa: 'aa'}}], {a: {aa: 'aa'}, b: {bb: 'bb'}}],
        [[{a: {aa: 'aa'}}, {a: {bb: 'bb'}}], {a: {aa: 'aa', bb: 'bb'}}],
        [[{a: ['a', 'b']}, {a: ['c']}], {a: ['c']}],
        [[{a: [{aa: 'aa'}, {bb: 'bb'}]}, {a: [{ccc: 'ccc'}, {ddd: 'ddd'}]}], {a: [{ccc: 'ccc'}, {ddd: 'ddd'}]}]
    ])('should correct merge %o to %o', (objects, expected) => {
        expect(putils.merge(...objects)).toStrictEqual(expected);
    });
    it.each([
        [[[]]],
        [[[1]]],
        [[['qwe']]],
        [[['1de', 2, 3], ['foo']]],
        [[[{foo: 'foo'}]]],
        [[]],
        [[undefined]],
        [[null]],
        [[null, 'wer']],
        [[{a: 'a'}, null]],
        [[{a: 'a'}, NaN]],
        [[NaN, {a: 'a'}]],
        [[0, {a: 'a'}]],
        [['', {a: 'a'}]],
        [[undefined, {a: {aa: 'aa'}}]],
        [[{}, {a: {aa: 'aa'}}, undefined]][[NaN]],
        [[0]],
        [[123]],
        [['']],
        [['qw']],
        [[[1], 34]],
        [[[1], 'wer']],
        [[[1], null]],
        [[undefined, {foo: 'foo'}]],
        [[null, {foo: 'foo'}]],
        [[NaN, {foo: 'foo'}]],
        [[0, {foo: 'foo'}]],
        [[123, {foo: 'foo'}]],
        [['', {foo: 'foo'}]],
        [['qw', {foo: 'foo'}]],
        [[[], {ude: 'ude'}]],
        [[['1de'], {foo: 'foo'}]]
    ])('should throw exception for merge %o to %o', (objects) => {
        try {
            putils.merge.call(null, objects);
        } catch (error) {
            expect(error.message).toEqual('Every argument should be with type "object"');
        }
    });
});
