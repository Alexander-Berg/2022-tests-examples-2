/* eslint-env node, mocha */
import * as assert from 'assert';

import {getImageSizesByScaleFactor} from '@div2/common/news/helpers';

describe('news helpers getImageSizesByScaleFactor', () => {
    it('should correctly generate sizes string', () => {
        assert.strictEqual(getImageSizesByScaleFactor([244, 122]), '244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 0), '244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 1), '244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 1.1), '366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 1.5), '366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 1.6), '488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 2), '488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 2.1), '732.366.1.avatars,488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 3), '732.366.1.avatars,488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 3.1), '976.488.1.avatars,732.366.1.avatars,488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 4), '976.488.1.avatars,732.366.1.avatars,488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([244, 122], 5), '976.488.1.avatars,732.366.1.avatars,488.244.1.avatars,366.183.1.avatars,244.122.1.avatars');

        assert.strictEqual(getImageSizesByScaleFactor([256, 128]), '256.128.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([256, 128], ''), '256.128.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([256, 128], '1.5'), '384.192.1.avatars,256.128.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([256, 128], '1.6'), '512.256.1.avatars,384.192.1.avatars,256.128.1.avatars');
        assert.strictEqual(getImageSizesByScaleFactor([256, 128], 5), '1024.512.1.avatars,768.384.1.avatars,512.256.1.avatars,384.192.1.avatars,256.128.1.avatars');
    });
});
