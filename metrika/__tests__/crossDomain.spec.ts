/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';

import * as browser from '@src/utils/browser';

import * as globalStorage from '@src/storage/global';
import * as localStorage from '@src/storage/localStorage';

import { SenderInfo } from '@src/sender/SenderInfo';
import { CounterOptions } from '@src/utils/counterOptions';
import { DEFAULT_COUNTER_TYPE } from '@src/providers/counterOptions';
import { crossDomain } from '../crossDomain';
import * as utils from '../utils';

describe('crossDomain midlleware', () => {
    let isAndroidWebView: any;
    let getValUtils: any;
    let isITPDisabled: any;
    let isFFVersion: any;
    let globalLocalStorage: any;

    const fakeWindow = {} as any as Window;
    let counterId = 1;
    const getCounterOptions = (): CounterOptions => {
        counterId += 1;
        return { id: counterId, counterType: DEFAULT_COUNTER_TYPE };
    };
    let isEU = 0;
    const next = sinon.fake();
    let getGlobalStorage: any;
    const setValSpy = sinon.spy();
    const generalFake = sinon.fake();
    const senderParams: SenderInfo = {
        brInfo: {
            ctx: generalFake,
            getVal: generalFake,
            setVal: setValSpy,
            setOrNot: generalFake,
            serialize: generalFake,
        } as any,
    };

    beforeEach(() => {
        isAndroidWebView = sinon.stub(browser, 'isAndroidWebView');
        isITPDisabled = sinon.stub(utils, 'isITPDisabled');
        isFFVersion = sinon.stub(utils, 'isFFVersion');

        getGlobalStorage = sinon
            .stub(globalStorage, 'getGlobalStorage')
            .returns({
                getVal: (name: string) => {
                    return name === 'isEU' ? isEU : true;
                },
            } as any);

        globalLocalStorage = sinon
            .stub(localStorage, 'globalLocalStorage')
            .returns({ isBroken: false } as any);

        getValUtils = sinon.stub(utils, 'getVal');
    });

    afterEach(() => {
        isAndroidWebView.restore();
        isITPDisabled.restore();
        isFFVersion.restore();

        getGlobalStorage.restore();
        globalLocalStorage.restore();
        getValUtils.restore();
        next.resetHistory();
        setValSpy.resetHistory();
    });

    it('should return empty middleware object if all conditions are wrong', () => {
        globalLocalStorage.returns({ isBroken: true } as any);
        isITPDisabled.returns(true);
        isFFVersion.returns(false);
        isAndroidWebView.returns(true);
        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );
        chai.expect(middleware).to.be.deep.eq({});
    });

    it('should return non-empty middleware object conditions are ok', () => {
        isITPDisabled.returns(false);
        isFFVersion.returns(true);
        isAndroidWebView.returns(false);
        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );
        chai.expect(middleware.afterRequest).to.be.not.undefined;
        chai.expect(middleware.beforeRequest).to.be.not.undefined;
    });

    it('should not call stabbed features if isEU flag is set', () => {
        isEU = 1;
        isITPDisabled.returns(false);
        isFFVersion.returns(true);
        isAndroidWebView.returns(false);
        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );

        if (middleware && middleware.beforeRequest && middleware.afterRequest) {
            middleware.beforeRequest(senderParams, next);
            middleware.afterRequest(senderParams, next);
        }
        sinon.assert.calledTwice(next);
        sinon.assert.notCalled(getValUtils);
    });

    it.skip('check PP feature', () => {
        isEU = 0;

        isAndroidWebView.returns(false);

        globalLocalStorage.returns({ isBroken: true } as any);
        isITPDisabled.returns(true);
        isFFVersion.returns(false);

        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );

        if (middleware && middleware.afterRequest && middleware.beforeRequest) {
            middleware.afterRequest(senderParams, next);
            middleware.beforeRequest(senderParams, next);
        }
        sinon.assert.calledTwice(next);

        const calls = getValUtils
            .getCalls()
            .map((i: any) => i.args)
            .filter((i: any) => i.indexOf('pp') !== -1);

        chai.expect(calls.length, 'getVal for PP called twice').to.be.equal(2);
        chai.expect(
            calls[0].length,
            'getVal for PP called w/o brInfo',
        ).to.be.equal(7);
        chai.expect(
            calls[1].length,
            'getVal for PP called with brInfo',
        ).to.be.equal(8);
    });

    it('check PU feature', () => {
        isEU = 0;

        isAndroidWebView.returns(true);

        globalLocalStorage.returns({ isBroken: true } as any);
        isITPDisabled.returns(false);
        isFFVersion.returns(true);

        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );

        if (middleware && middleware.afterRequest && middleware.beforeRequest) {
            middleware.afterRequest(senderParams, next);
            middleware.beforeRequest(senderParams, next);
        }

        chai.expect(next.calledTwice, 'next called twice').to.be.true;

        const calls = getValUtils
            .getCalls()
            .map((i: any) => i.args)
            .filter((i: any) => i.indexOf('pu') !== -1);

        chai.expect(calls.length, 'getVal for PU called twice').to.be.equal(2);
        chai.expect(
            calls[0].length,
            'getVal for PU called w/o brInfo',
        ).to.be.equal(7);
        chai.expect(
            calls[1].length,
            'getVal for PU called with brInfo',
        ).to.be.equal(8);
    });

    it('check ZZ feature', () => {
        isEU = 0;

        isAndroidWebView.returns(true);

        globalLocalStorage.returns({ isBroken: false } as any);
        isITPDisabled.returns(false);
        isFFVersion.returns(true);

        const middleware = crossDomain(
            fakeWindow,
            'provider',
            getCounterOptions(),
        );

        if (middleware && middleware.afterRequest && middleware.beforeRequest) {
            middleware.afterRequest(senderParams, next);
            middleware.beforeRequest(senderParams, next);
        }

        chai.expect(next.calledTwice, 'next called twice').to.be.true;
        const calls = getValUtils
            .getCalls()
            .map((i: any) => i.args)
            .filter((i: any) => i.indexOf('zzlc') !== -1);

        chai.expect(calls.length, 'getVal for ZZ called twice').to.be.equal(2);
        chai.expect(
            calls[0].length,
            'getVal for ZZ called w/o brInfo',
        ).to.be.equal(7);
        chai.expect(
            calls[1].length,
            'getVal for ZZ called with brInfo',
        ).to.be.equal(8);
    });
});
