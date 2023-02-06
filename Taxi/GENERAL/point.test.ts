import {describe, expect, it} from 'tests/jest.globals';

import {formatPointCoordinates} from './point';

describe('formatPointCoordinates()', () => {
    it('should format point to string', async () => {
        const point = formatPointCoordinates([37.521749698748046, 55.7577]);

        expect(point).toEqual('55.757700, 37.521750');
    });
});
