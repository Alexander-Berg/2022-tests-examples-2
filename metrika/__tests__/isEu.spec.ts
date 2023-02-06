import * as sinon from 'sinon';
import * as globalStorage from '@src/storage/global';
import * as localStorage from '@src/storage/localStorage';
import {
    FAKE_HIT_CACHE_KEY,
    FAKE_HIT_PARAMS_KEY,
} from '@src/providers/fakeHit/const';
import * as debug from '@src/providers/debugger/dispatchEvent';
import { IS_EU_CONFIG_KEY } from '@src/middleware/counterFirstHit';
import { isEuFn } from '@src/providers/isEu';
import * as cookie from '@src/storage/cookie';

describe('set isEU', () => {
    const sandbox = sinon.createSandbox();
    const winInfo = {} as any;

    let globalEu: number | undefined;
    let getGlobalValSpy: sinon.SinonSpy;
    let setGlobalValSpy: sinon.SinonSpy;

    let isGdprCookie: number | undefined;
    let getCookieSpy: sinon.SinonSpy;

    const valueFromLocalStorage = 1;
    let localSettings: any;
    let getLocalValSpy: any;

    beforeEach(() => {
        sandbox.stub(debug, 'dispatchDebuggerEvent');
        globalEu = undefined;
        isGdprCookie = undefined;
        localSettings = undefined;

        getGlobalValSpy = sandbox.spy(() => globalEu);
        setGlobalValSpy = sandbox.spy((name, value) => {
            globalEu = value;
        });
        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            getVal: getGlobalValSpy,
            setVal: setGlobalValSpy,
        } as any);
        getCookieSpy = sandbox.spy(() => isGdprCookie);
        sandbox.stub(cookie, 'getCookie').callsFake(getCookieSpy);
        getLocalValSpy = sandbox.spy(() => localSettings);
        sandbox.stub(localStorage, 'globalLocalStorage').returns({
            getVal: getLocalValSpy,
        } as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it(`has isEu in globalConfig`, () => {
        globalEu = 1;

        isEuFn(winInfo);
        sinon.assert.calledWith(getGlobalValSpy, IS_EU_CONFIG_KEY);
    });

    it(`has isEu in localStorage`, () => {
        localSettings = {
            [FAKE_HIT_PARAMS_KEY]: {
                eu: valueFromLocalStorage,
            },
        } as any;

        isEuFn(winInfo);
        sinon.assert.calledWith(getLocalValSpy, FAKE_HIT_CACHE_KEY);
        sinon.assert.calledWith(
            setGlobalValSpy,
            IS_EU_CONFIG_KEY,
            valueFromLocalStorage,
        );
    });

    it(`has not isEu`, () => {
        isEuFn(winInfo);
        sinon.assert.calledWith(getLocalValSpy, FAKE_HIT_CACHE_KEY);
        sinon.assert.notCalled(setGlobalValSpy);
    });
});
