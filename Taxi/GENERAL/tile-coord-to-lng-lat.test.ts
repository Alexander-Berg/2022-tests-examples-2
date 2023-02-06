import {describe, expect, it} from 'tests/jest.globals';

import {tileCoordToLngLat} from './tile-coord-to-lng-lat';

describe('tileCoordToLngLat()', () => {
    it('should return true coordinates by x, y, z', async () => {
        const x = 2473;
        const y = 1282;
        const z = 12;

        const coords = tileCoordToLngLat(x, y, z);

        expect(coords).toEqual([
            [37.353515625, 55.85644056569717],
            [37.44140625, 55.80697401730049]
        ]);
    });
});
