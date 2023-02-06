import fs from 'fs';

import {serviceResolve} from '@/src/lib/resolve';

import {getRectsByBuffer} from './index';

describe('Rectangles JSON', () => {
    it('should return JSON by path', async () => {
        const json = await getRectsByBuffer(
            fs.readFileSync(serviceResolve('./src/service/opencv-table-recognition/utils/aligned-fragment.png'))
        );

        const expectedJSON = await fs.readFileSync(
            serviceResolve('./src/service/opencv-table-recognition/utils/aligned-fragment.json'),
            'utf8'
        );

        expect(JSON.stringify(json, null, '\t')).toBe(expectedJSON);
    });
});
