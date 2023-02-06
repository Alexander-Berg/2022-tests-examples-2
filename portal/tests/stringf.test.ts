import { stringf } from '../stringf';

describe('home.stringf', function() {
    it('replaces', function() {
        expect(stringf('')).toEqual('');
        expect(stringf('', 'apple')).toEqual('');
        expect(stringf('%s')).toEqual('');
        expect(stringf('%s', undefined)).toEqual('');
        expect(stringf('%s', null)).toEqual('');
        expect(stringf('%s', 'apple')).toEqual('apple');
        expect(stringf('%s - %s', 'apple')).toEqual('apple - ');
        expect(stringf('%s - %s', 'apple', 'juice')).toEqual('apple - juice');
    });
});
