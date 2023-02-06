import * as chai from 'chai';
import * as sinon from 'sinon';
import { host } from '@src/config';
import { browserInfo } from '@src/utils/browserInfo';
import * as time from '@src/utils/time';
import * as localStorage from '@src/storage/localStorage';
import * as globalStorage from '@src/storage/global';
import {
    WEBVISOR_TYPE_WEBVISOR_FIRST,
    WEBVISOR_TYPE_KEY,
} from '@private/src/sender/webvisor';
import { CounterOptions } from '@src/utils/counterOptions';
import { SenderInfo } from '@src/sender/SenderInfo';
import { telemetry } from '@src/utils/telemetry/telemetry';
import * as inject from '@src/inject';
import { TELEMETRY_FEATURE } from '@generated/features';
import { retransmit } from '../retransmit';
import * as state from '../state';

describe('retransmit middleware', () => {
    const now = 1123112;
    const HID = 123123123113;
    const sandbox = sinon.createSandbox();

    let localStorageStub: sinon.SinonStub<
        Parameters<typeof localStorage.globalLocalStorage>,
        localStorage.LocalStorage
    >;
    let reqList: Record<string, state.RetransmitInfo> = {};
    const localStorageSetValMock = sandbox.stub();
    const mockLocalStorage = {
        setVal: localStorageSetValMock,
    } as unknown as localStorage.LocalStorage;

    beforeEach(() => {
        sandbox.stub(inject, 'flags').value({
            ...inject.flags,
            [TELEMETRY_FEATURE]: true,
        });
        sandbox.stub(time, 'TimeOne').returns(<R>() => now as unknown as R);
        sandbox.stub(state, 'getRetransmitLsState').value(() => reqList);
        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            getVal: sandbox.stub().returns(HID),
        } as unknown as globalStorage.GlobalStorage);
        localStorageStub = sandbox
            .stub(localStorage, 'globalLocalStorage')
            .returns(mockLocalStorage);
    });

    afterEach(() => {
        reqList = {};
        sandbox.restore();
        localStorageSetValMock.resetHistory();
    });

    it('skips empty urlParams', () => {
        const ctx = {} as Window;
        const senderParams = {
            browserInfo: browserInfo({}),
        } as SenderInfo;
        const counterOptions = {} as CounterOptions;
        const next = sandbox.stub();

        const middleware = retransmit();
        middleware(ctx, 'a', counterOptions).beforeRequest!(senderParams, next);

        sinon.assert.calledOnce(next);
        sinon.assert.notCalled(localStorageStub);
    });

    it('skips empty brInfo', () => {
        const ctx = {} as Window;
        const senderParams = {
            urlParams: {},
        } as SenderInfo;
        const counterOptions = {} as CounterOptions;
        const next = sandbox.stub();

        const middleware = retransmit();
        middleware(ctx, 'a', counterOptions).beforeRequest!(senderParams, next);

        sinon.assert.calledOnce(next);
        sinon.assert.notCalled(localStorageStub);
    });

    it('skips not allowed webvisor type', () => {
        const ctx = {} as Window;
        const senderParams = {
            urlParams: {
                [WEBVISOR_TYPE_KEY]: 'some-unknown-wv-type',
            },
            browserInfo: browserInfo({}),
        } as SenderInfo;
        const counterOptions = {} as CounterOptions;
        const next = sandbox.stub();

        const middleware = retransmit();
        middleware(ctx, 'a', counterOptions).beforeRequest!(senderParams, next);

        sinon.assert.calledOnce(next);
        sinon.assert.notCalled(localStorageStub);
    });

    it('registers request for future retransmit and removes it after retransmit', () => {
        const ctx = {
            Array,
        } as Window;
        const senderParams = {
            urlParams: {
                [WEBVISOR_TYPE_KEY]: WEBVISOR_TYPE_WEBVISOR_FIRST,
            },
            brInfo: browserInfo({}),
            telemetry: telemetry({}),
        } as SenderInfo;
        const counterOptions: CounterOptions = {
            id: 1234,
            counterType: '0',
        };
        const next = sandbox.stub();

        const middleware = retransmit()(ctx, 'a', counterOptions);
        middleware.beforeRequest!(senderParams, next);
        sinon.assert.calledOnce(localStorageSetValMock);
        let [key, newLsState] = localStorageSetValMock.getCall(0).args;

        chai.expect(key).to.equal(state.RETRANSMIT_KEY);
        chai.expect(newLsState).to.be.deep.eq({
            '1': {
                counterType: '0',
                counterId: 1234,
                protocol: 'http:',
                host,
                resource: 'webvisor',
                postParams: undefined,
                time: now,
                params: {
                    'wv-type': WEBVISOR_TYPE_WEBVISOR_FIRST,
                },
                browserInfo: {
                    rqnl: 1,
                },
                telemetry: {
                    rqnl: 1,
                },
                ghid: HID,
            } as Partial<state.RetransmitInfo>,
        });

        sinon.assert.calledOnce(next);
        next.resetHistory();

        middleware.afterRequest!(senderParams, next);

        sinon.assert.calledTwice(localStorageSetValMock);
        [key, newLsState] = localStorageSetValMock.getCall(1).args;
        sinon.assert.calledOnce(next);
        chai.expect(key).to.equal(state.RETRANSMIT_KEY);
        chai.expect(newLsState).to.be.empty;
    });
});
