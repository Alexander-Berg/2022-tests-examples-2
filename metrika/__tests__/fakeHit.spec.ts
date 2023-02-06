import * as chai from 'chai';
import * as sinon from 'sinon';
import * as localStorage from '@src/storage/localStorage';
import * as timeUtils from '@src/utils/time';
import * as sender from '@src/sender';
import { WATCH_URL_PARAM, WATCH_REFERER_PARAM } from '@src/sender/watch';
import { fakeHit } from '../fakeHit';
import { FAKE_HIT_COUNTER } from '../..';
import {
    FAKE_HIT_PARAMS_KEY,
    FAKE_HIT_CACHE_KEY,
    FAKE_HIT_TIME_KEY,
    FAKE_HIT_BK_PARAMS_KEY,
} from '../const';

describe('fakeHit', () => {
    const stamp = 100;
    const response = {
        settings: { a: 1 },
        userData: { b: 2 },
    };
    const sandbox = sinon.createSandbox();
    const mySender = sinon.stub().returns(
        Promise.resolve({
            settings: { a: 1 },
            userData: { b: 2 },
        }),
    );
    const ls = {
        getVal: sinon.stub(),
        setVal: sinon.stub(),
    };
    let localStorageMock: any;
    let timeUtilsMock: any;
    let senderStub: any;

    beforeEach(() => {
        senderStub = sandbox.stub(sender, 'getSender');
        senderStub.returns(mySender);
        timeUtilsMock = sandbox.stub(timeUtils, 'TimeOne');
        timeUtilsMock.returns(() => stamp);
        localStorageMock = sandbox.stub(localStorage, 'globalLocalStorage');
        localStorageMock.returns(ls as any);
    });

    afterEach(() => {
        sandbox.restore();
        ls.getVal.resetHistory();
        ls.setVal.resetHistory();
    });

    it('returns data from cahce if data is set in ls', () => {
        const cache = {
            time: 0,
        };
        ls.getVal.returns(cache);
        return fakeHit({} as any, true).then((result) => {
            chai.expect(ls.getVal.calledWith(FAKE_HIT_CACHE_KEY)).to.be.true;
            chai.expect(result).to.equal(cache);
        });
    });

    it('Makes fake hit', () => {
        const href = 'http://example.com';
        const referrer = 'https://google.com';
        return fakeHit(
            {
                JSON,
                location: {
                    href,
                },
                document: {
                    referrer,
                },
            } as any,
            false,
        ).then(() => {
            const [key, setCache] = ls.setVal.getCall(0).args;
            chai.expect(key).to.equal(FAKE_HIT_CACHE_KEY);
            chai.expect(setCache).to.deep.equal({
                [FAKE_HIT_TIME_KEY]: stamp,
                [FAKE_HIT_PARAMS_KEY]: response.settings,
                [FAKE_HIT_BK_PARAMS_KEY]: response.userData,
            });
            const [senderOptions, counterOptions] = mySender.getCall(0).args;

            chai.expect(counterOptions).to.deep.equal({
                id: FAKE_HIT_COUNTER,
                counterType: '0',
            });
            chai.expect(senderOptions.urlParams).to.deep.equal({
                [WATCH_URL_PARAM]: href,
                [WATCH_REFERER_PARAM]: referrer,
            });
        });
    });
});
