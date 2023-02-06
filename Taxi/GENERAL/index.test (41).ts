import crypto from 'crypto';
import fs from 'fs';
import nock from 'nock';
import tmp from 'tmp';

import {AvatarsProvider, AvatarsUploadResponse} from './avatars-provider';

const SERVICE_TICKET = 'SERVICE_TICKET';
const NAMESPACE = 'namespace';
const GROUP_ID = 123;
const IMAGE_NAME = 'image';
const IMAGE_EXTENSION = 'jpg';
const IMAGE_WIDTH = 512;
const IMAGE_HEIGHT = 512;
const IMAGE_SIZE = 10; // 256K

const COMMON_PARAMS = {
    getServiceTicket: async () => SERVICE_TICKET,
    namespace: NAMESPACE
};

describe('package "avatars-provider"', () => {
    beforeAll(async () => {
        nock.disableNetConnect();
        nock.enableNetConnect(/localhost/);
    });

    afterAll(async () => {
        nock.enableNetConnect();
    });

    afterEach(async () => {
        nock.cleanAll();
    });

    it('should build correct download url', () => {
        const testingInternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: false, isExternal: false});
        const testingExternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: false, isExternal: true});
        const productionInternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: true, isExternal: false});
        const productionExternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: true, isExternal: true});

        expect(testingInternal.getDownloadUrl(GROUP_ID, IMAGE_NAME)).toEqual(
            `https://avatars-int.mdst.yandex.net/get-${NAMESPACE}/${GROUP_ID}/${IMAGE_NAME}/%s`
        );
        expect(testingExternal.getDownloadUrl(GROUP_ID, IMAGE_NAME)).toEqual(
            `https://avatars.mdst.yandex.net/get-${NAMESPACE}/${GROUP_ID}/${IMAGE_NAME}/%s`
        );
        expect(productionInternal.getDownloadUrl(GROUP_ID, IMAGE_NAME)).toEqual(
            `https://avatars-int.mds.yandex.net/get-${NAMESPACE}/${GROUP_ID}/${IMAGE_NAME}/%s`
        );
        expect(productionExternal.getDownloadUrl(GROUP_ID, IMAGE_NAME)).toEqual(
            `https://avatars.mds.yandex.net/get-${NAMESPACE}/${GROUP_ID}/${IMAGE_NAME}/%s`
        );
    });

    it('should build correct upload url', () => {
        const testingInternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: false, isExternal: false});
        const testingExternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: false, isExternal: true});
        const productionInternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: true, isExternal: false});
        const productionExternal = new AvatarsProvider({...COMMON_PARAMS, isProduction: true, isExternal: true});

        expect(testingInternal.getUploadUrl(IMAGE_NAME)).toEqual(
            `http://avatars-int.mdst.yandex.net:13000/put-${NAMESPACE}/${IMAGE_NAME}`
        );
        expect(testingExternal.getUploadUrl(IMAGE_NAME)).toEqual(
            `http://avatars-int.mdst.yandex.net:13000/put-${NAMESPACE}/${IMAGE_NAME}`
        );
        expect(productionInternal.getUploadUrl(IMAGE_NAME)).toEqual(
            `http://avatars-int.mds.yandex.net:13000/put-${NAMESPACE}/${IMAGE_NAME}`
        );
        expect(productionExternal.getUploadUrl(IMAGE_NAME)).toEqual(
            `http://avatars-int.mds.yandex.net:13000/put-${NAMESPACE}/${IMAGE_NAME}`
        );
    });

    it('should return md5 and image buffer from buffer', async () => {
        const provider = new AvatarsProvider({...COMMON_PARAMS});
        const imageBuffer = crypto.randomBytes(IMAGE_SIZE);
        const hash = crypto.createHash('md5');
        const md5 = hash.update(imageBuffer).digest('hex');
        const data = await provider.getImageBufferAndMd5(imageBuffer);

        expect(data.md5).toEqual(md5);
        expect(data.imageBuffer).toEqual(imageBuffer);
    });

    it('should return md5 and image buffer from stream', async () => {
        const provider = new AvatarsProvider({...COMMON_PARAMS});
        const tmpFile = tmp.fileSync({prefix: 'avatars-provider-test'});
        const imageBuffer = crypto.randomBytes(IMAGE_SIZE);
        const hash = crypto.createHash('md5');
        const md5 = hash.update(imageBuffer).digest('hex');
        fs.writeFileSync(tmpFile.name, imageBuffer);
        const stream = fs.createReadStream(tmpFile.name);
        const data = await provider.getImageBufferAndMd5(stream);
        tmpFile.removeCallback();

        expect(data.md5).toEqual(md5);
        expect(data.imageBuffer).toEqual(imageBuffer);
    });

    it('should post image to avatars service', async () => {
        nock('http://avatars-int.mdst.yandex.net:13000')
            .post(new RegExp(`/put-${NAMESPACE}/[\\w-]*`))
            .matchHeader('x-ya-service-ticket', SERVICE_TICKET)
            .reply(200, {
                'group-id': GROUP_ID,
                meta: {
                    'orig-format': IMAGE_EXTENSION,
                    'orig-size': {
                        x: IMAGE_WIDTH,
                        y: IMAGE_HEIGHT
                    },
                    'orig-size-bytes': IMAGE_SIZE
                }
            } as AvatarsUploadResponse);

        const provider = new AvatarsProvider({...COMMON_PARAMS});
        const imageBuffer = crypto.randomBytes(IMAGE_SIZE);
        const data = await provider.uploadImage(imageBuffer);

        expect(data.url).toMatch(
            new RegExp(`https://avatars-int.mdst.yandex.net/get-${NAMESPACE}/${GROUP_ID}/[\\w-]*/%s`)
        );

        expect(data.meta).toEqual({
            name: expect.any(String),
            width: IMAGE_WIDTH,
            height: IMAGE_HEIGHT,
            size: IMAGE_SIZE
        });
    });
});
