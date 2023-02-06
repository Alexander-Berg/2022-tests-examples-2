import * as chai from 'chai';
import * as sinon from 'sinon';
import { host } from '@src/config';
import * as time from '@src/utils/time';
import * as localStorage from '@src/storage/localStorage';
import * as globalStorage from '@src/storage/global';
import { getRetransmitRequestsRaw } from '../retransmit';
import * as state from '../state';

describe('getRetransmitRequests', () => {
    const now = 1123112;
    const HID = 123123123113;
    const CURRENT_HID = 123;
    let lsState: Record<string, Partial<state.RetransmitInfo>> = {};
    const mockLs = {
        getVal: () => lsState,
    } as unknown as localStorage.LocalStorage;
    const sandbox = sinon.createSandbox();
    let timeStub: sinon.SinonStub<
        [ctx: Window],
        <R>(fn: (a: time.TimeState) => R) => R
    >;
    let globalStorageStub: sinon.SinonStub<
        [ctx: Window],
        globalStorage.GlobalStorage
    >;
    let localStorageStub: sinon.SinonStub<
        [ctx: Window, nameSpace?: string | number, prefix?: string],
        localStorage.LocalStorage
    >;

    beforeEach(() => {
        timeStub = sandbox.stub(time, 'TimeOne');
        sandbox.stub(state, 'getRetransmitLsState').value(() => lsState);
        timeStub.returns(<R>() => now as unknown as R);
        globalStorageStub = sandbox.stub(globalStorage, 'getGlobalStorage');
        globalStorageStub.callsFake(() => {
            return {
                getVal: sinon.stub().returns(CURRENT_HID),
            } as any;
        });
        localStorageStub = sandbox.stub(localStorage, 'globalLocalStorage');
        localStorageStub.returns(mockLs);
    });

    afterEach(() => {
        lsState = {};
        sandbox.restore();
    });

    it('filters retransmit requests', () => {
        lsState = {
            '1': {
                counterId: 123,
                protocol: 'http:',
                host,
                resource: 'webvisor',
                time: now - 1000,
                postParams: null,
                counterType: '0',
                params: {
                    'wv-type': '4',
                },
                browserInfo: {
                    rqnl: 0,
                },
                telemetry: {
                    rqnl: 0,
                },
                ghid: CURRENT_HID,
            },
            '2': {
                counterId: 123,
                counterType: '0',
                protocol: 'http:',
                host,
                resource: 'webvisor',
                time: now - 1000,
                params: {
                    'wv-type': '4',
                },
                browserInfo: {
                    rqnl: 3,
                },
                telemetry: {
                    rqnl: 3,
                },
                ghid: HID,
            },
            '3': {
                counterId: 123,
                counterType: '0',
                protocol: 'http:',
                host,
                params: undefined,
                postParams: null,
                resource: 'watch',
                time: now - state.RETRANSMIT_EXPIRE * 2,
                browserInfo: {
                    rqnl: 0,
                },
                telemetry: {
                    rqnl: 0,
                },
                ghid: HID,
            },
            '4': {
                counterId: 123,
                params: undefined,
                postParams: null,
                counterType: '0',
                protocol: 'http:',
                host,
                resource: 'watch',
                time: now - 1000,
                browserInfo: {
                    rqnl: 2,
                },
                telemetry: {
                    rqnl: 2,
                },
                ghid: HID,
            },
            '5': {
                counterId: 123,
                params: undefined,
                postParams: null,
                counterType: '0',
                protocol: 'http:',
                host,
                resource: 'watch',
                time: now,
                browserInfo: {
                    rqnl: 2,
                },
                telemetry: {
                    rqnl: 2,
                },
                ghid: HID,
            },
        };

        const result = getRetransmitRequestsRaw({} as Window);
        chai.expect(result).to.be.deep.eq([
            {
                protocol: 'http:',
                counterType: '0',
                host,
                resource: 'watch',
                time: now - 1000,
                browserInfo: {
                    rqnl: 2,
                },
                telemetry: {
                    rqnl: 2,
                },
                ghid: HID,
                params: undefined,
                postParams: null,
                counterId: 123,
                retransmitIndex: 4,
            },
        ] as Partial<state.RetransmitInfo>[]);
        chai.expect(lsState['4'].d).to.be.ok;
    });
});
