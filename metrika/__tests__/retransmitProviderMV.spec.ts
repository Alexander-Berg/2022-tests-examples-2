import * as chai from 'chai';
import * as sinon from 'sinon';
import { host } from '@src/config';
import { browserInfo } from '@src/utils/browserInfo';
import * as time from '@src/utils/time';
import * as localStorage from '@src/storage/localStorage';
import * as globalStorage from '@src/storage/global';
import { SenderInfo } from '@src/sender/SenderInfo';
import { CounterOptions } from '@src/utils/counterOptions';
import { telemetry } from '@src/utils/telemetry/telemetry';
import * as inject from '@src/inject';
import { TELEMETRY_FEATURE } from '@generated/features';
import * as state from '../state';
import { retransmitProviderMiddleware } from '../retransmit';

describe('retransmitProviderMiddleware', () => {
    const now = 1123112;
    const HID = 123123123113;
    const sandbox = sinon.createSandbox();

    let reqList: Record<string, state.RetransmitInfo> = {};
    const localStorageSetValMock = sandbox.stub();
    const mockLocalStorage = {
        setVal: localStorageSetValMock,
    } as unknown as localStorage.LocalStorage;

    beforeEach(() => {
        reqList = {};
        sandbox.stub(inject, 'flags').value({
            ...inject.flags,
            [TELEMETRY_FEATURE]: true,
        });
        sandbox.stub(state, 'getRetransmitLsState').value(() => reqList);
        sandbox
            .stub(time, 'TimeOne')
            .returns(<R>(fn: (a: any) => R) => now as unknown as R);
        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            getVal: sinon.stub().returns(HID),
        } as unknown as globalStorage.GlobalStorage);
        sandbox
            .stub(localStorage, 'globalLocalStorage')
            .returns(mockLocalStorage);
    });

    afterEach(() => {
        reqList = {};
        sandbox.restore();
        localStorageSetValMock.resetHistory();
    });

    it('Increases "rnql" and afterwards removes request from ls', () => {
        const ctx = {
            Array,
        } as Window;
        const counterOptions = {} as CounterOptions;
        const brInfoAndTelemetryState: state.RetransmitInfo['browserInfo'] = {
            [state.RETRANSMIT_BRINFO_AND_TELEMETRY_KEY]: 1,
        };
        const senderParams: SenderInfo = {
            brInfo: browserInfo(brInfoAndTelemetryState),
            retransmitIndex: 4,
            telemetry: telemetry(brInfoAndTelemetryState),
        };
        reqList = {
            '4': {
                protocol: 'http:',
                host,
                resource: 'webvisor',
                time: now,
                params: {
                    'wv-type': '4',
                },
                browserInfo: {
                    rqnl: 1,
                },
                telemetry: {
                    rqnl: 1,
                },
                ghid: HID,
            } as unknown as state.RetransmitInfo,
        };
        const next = sinon.stub();
        const middleware = retransmitProviderMiddleware()(
            ctx,
            'a',
            counterOptions,
        );

        middleware.beforeRequest!(senderParams, next);

        chai.expect(next.called).to.be.true;
        chai.expect(
            senderParams.brInfo!.getVal(
                state.RETRANSMIT_BRINFO_AND_TELEMETRY_KEY,
            ),
        ).to.equal(2);
        sinon.assert.calledOnce(localStorageSetValMock);
        let [lsKey, newLsState] = localStorageSetValMock.getCall(0).args;
        chai.expect(lsKey).to.equal(state.RETRANSMIT_KEY);
        chai.expect(newLsState).to.deep.equal({
            '4': {
                protocol: 'http:',
                host,
                resource: 'webvisor',
                time: now,
                params: {
                    'wv-type': '4',
                },
                browserInfo: {
                    rqnl: 2,
                },
                telemetry: {
                    rqnl: 2,
                },
                ghid: HID,
            },
        });

        next.resetHistory();
        localStorageSetValMock.resetHistory();

        middleware.afterRequest!(senderParams, next);
        sinon.assert.calledOnce(next);
        sinon.assert.calledOnce(localStorageSetValMock);
        [lsKey, newLsState] = localStorageSetValMock.getCall(0).args;
        chai.expect(lsKey).to.equal(state.RETRANSMIT_KEY);
        chai.expect(newLsState).to.deep.equal({});
    });
});
