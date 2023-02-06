import { KeyStorage } from '../types';
import {splitKeystorage} from './split-keystorage';

describe('splitKeystorage', () => {
    it('should split keystorage by chunks', () => {
        const foo = {key: 'foo', value: 'foo', meta: {}};
        const bar = {key: 'bar', value: 'bar', meta: {}};
        const baz = {key: 'baz', value: 'baz', meta: {}};

        const storage: KeyStorage = [foo, bar, baz];

        expect(splitKeystorage([], 100)).toStrictEqual([]);
        expect(splitKeystorage(storage, 9)).toStrictEqual([[foo, bar, baz]]);
        expect(splitKeystorage(storage, 6)).toStrictEqual([[foo, bar], [baz]]);
        expect(splitKeystorage(storage, 5)).toStrictEqual([[foo], [bar], [baz]]);
    });

    it('should throw error when key value more than chunk size', () => {
        const storage: KeyStorage = [
            {key: 'foo', value: 'foo', meta: {}},
        ];

        expect(() => splitKeystorage(storage, 2)).toThrow();
    });
});
