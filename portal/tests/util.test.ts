/* eslint-env node, mocha */
import * as assert from 'assert';

import * as Utils from '../util';

describe('string utility functions', () => {
    it('should correctly extract substring', () => {
        assert.equal(Utils.substring(''), '');
        assert.equal(Utils.substring('ab', 0, 2), 'ab'.slice(0, 2));
        assert.equal(Utils.substring('abc', 0, 2), 'abc'.slice(0, 2));
        assert.equal(Utils.substring('abc', 0, 3), 'abc'.slice(0, 3));
        assert.equal(Utils.substring('𝐀a𝐁b💩', 0, 1), '𝐀');
        assert.equal(Utils.substring('𝐀a𝐁b💩', 4, 5), '💩');
        assert.equal(Utils.substring('𝐀a𝐁b💩', 0, 3), '𝐀a𝐁');
        assert.equal(Utils.substring('𝐀a𝐁b💩', 2, 5), '𝐁b💩');
        assert.equal(Utils.substring('𝐀a𝐁b💩', 0, 5), '𝐀a𝐁b💩');
        assert.equal(Utils.substring('a𝐀𝐁b💩', 0, 5), 'a𝐀𝐁b💩');
    });
});

describe('shuffle', () => {
    it('should depend on Math.random()', () => {
        const xs = [0, 1, 2, 3, 4, 5];
        const random = Math.random;

        Math.random = () => 0;
        assert.deepEqual(Utils.shuffle(xs), xs);

        Math.random = () => 0.99;
        assert.deepEqual(Utils.shuffle(xs), [5, 0, 1, 2, 3, 4]);

        Math.random = random;
    });
});
