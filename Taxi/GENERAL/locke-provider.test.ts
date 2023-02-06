import {createStream, Logger} from '@lavka-js-toolbox/logger';
import nock from 'nock';

import {YT_LOCKE_HOST, YT_PARAMETERS_HEADER, YTParameters} from './locke-client';
import {LockeProvider} from './locke-provider';

const YT_HOST = 'some.yt.host';

describe('package "mutex" - LockeProvider()', () => {
    let provider: LockeProvider;
    let logger: Logger;
    const noopTransport = () => {};

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

    beforeEach(async () => {
        nock(YT_LOCKE_HOST).get('/hosts').reply(200, [YT_HOST]);

        logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport: noopTransport})
        });

        provider = new LockeProvider({
            logger,
            token: 'token',
            path: '//home/dir',
            key: 'some_key'
        });
    });

    it('should create lock with default ttl', async () => {
        const ttl = Date.now() + 5000;

        nock(`http://${YT_HOST}`)
            .post('/api/v3/create')
            .matchHeader(
                YT_PARAMETERS_HEADER,
                makeYTParamsHeaderMatcher(({type, path, attributes}) => {
                    const expirationTime = attributes?.expiration_time as number;
                    return Math.abs(expirationTime - ttl) < 2000 && type === 'table' && path === '//home/dir/some_key';
                })
            )
            .reply(200);

        await provider.createLock();

        expect(nock.pendingMocks()).toHaveLength(0);
    });

    it('should create lock with manual ttl', async () => {
        const lockTimeoutMs = 10000;

        provider = new LockeProvider({
            logger,
            lockTimeoutMs,
            token: 'token',
            path: '//home/dir',
            key: 'some_key'
        });

        const ttl = Date.now() + lockTimeoutMs;

        nock(`http://${YT_HOST}`)
            .post('/api/v3/create')
            .matchHeader(
                YT_PARAMETERS_HEADER,
                makeYTParamsHeaderMatcher(({type, path, attributes}) => {
                    const expirationTime = attributes?.expiration_time as number;
                    return Math.abs(expirationTime - ttl) < 2000 && type === 'table' && path === '//home/dir/some_key';
                })
            )
            .reply(200);

        await provider.createLock();

        expect(nock.pendingMocks()).toHaveLength(0);
    });

    it('should release lock', async () => {
        nock(`http://${YT_HOST}`)
            .post('/api/v3/remove')
            .matchHeader(
                YT_PARAMETERS_HEADER,
                makeYTParamsHeaderMatcher(({path, force}) => path === '//home/dir/some_key' && force === true)
            )
            .reply(200);

        await provider.releaseLock();

        expect(nock.pendingMocks()).toHaveLength(0);
    });

    it('should check exist lock', async () => {
        nock(`http://${YT_HOST}`)
            .get('/api/v3/exists')
            .matchHeader(
                YT_PARAMETERS_HEADER,
                makeYTParamsHeaderMatcher(({path}) => path === '//home/dir/some_key')
            )
            .reply(200, 'false', {'content-type': 'application/json'});

        const isExist = await provider.isLockExist();
        expect(isExist).toBe(false);
        expect(nock.pendingMocks()).toHaveLength(0);
    });
});

function makeYTParamsHeaderMatcher(matchYTParams: (ytParams: YTParameters) => boolean) {
    return (ytParamsString: string) => {
        const ytParams: YTParameters = JSON.parse(ytParamsString);
        return matchYTParams(ytParams);
    };
}
