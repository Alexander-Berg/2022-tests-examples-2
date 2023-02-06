/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
import { HomeLogo } from '@block/home-logo/home-logo.view';
import * as reqs from './mocks/index';

describe('home-logo', function() {
    it('default', function() {
        const html = execView(HomeLogo, {}, reqs.std);

        expect(html).toMatchSnapshot();
    });

    it('custom', function() {
        const html = execView(HomeLogo, {}, reqs.custom);

        expect(html).toMatchSnapshot();
    });

    it('custom-offsets', function() {
        const html = execView(HomeLogo, {}, reqs.customOffsets);

        expect(html).toMatchSnapshot();
    });
});
