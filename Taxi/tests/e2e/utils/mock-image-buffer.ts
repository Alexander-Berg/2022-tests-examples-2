import nock from 'nock';

import {generateImageBufferFromUrl} from './generate-image-buffer-from-url';

export function mockImageBuffer(host: string, url: string) {
    const scope = nock(host).get(url).reply(200, generateImageBufferFromUrl(url), {'content-type': 'image/png'});

    return scope;
}
