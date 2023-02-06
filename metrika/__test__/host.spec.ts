import * as sinon from 'sinon';
import { expect } from 'chai';
import * as countOpt from '@src/utils/counterOptions';
import { InternalSenderInfo } from '@src/sender/SenderInfo';
import {
    ROSTELECOM_KEY,
    MEGAFON_KEY,
    READY_STATE,
    CSP_WAIT,
} from '@src/providers/internetServiceProvider/const';
import { getITPProviderHostPrefix } from '../host';
import * as utils from '../utils';

describe('isp ITP host prefix', () => {
    const sandbox = sinon.createSandbox();
    const FNVHashStub = 1234;
    const counterOptions: countOpt.CounterOptions = {
        counterType: '0',
        id: FNVHashStub,
    };
    const setValStub = sandbox.stub();
    const counterKey = 'counterKey';
    const win = {} as any;
    let getSateStub: sinon.SinonStub<any, any>;
    let getFNVHashStub: sinon.SinonStub<any, any>;
    let senderParams: InternalSenderInfo;
    beforeEach(() => {
        getSateStub = sandbox.stub(utils, 'getState');
        getFNVHashStub = sandbox
            .stub(utils, 'getFNVHash')
            .callsFake((_, __) => FNVHashStub);
        getSateStub.returns({ [counterKey]: {} });
        senderParams = {
            debugStack: [],
            brInfo: {
                setVal: setValStub,
            } as any,
        };
        sandbox.stub(countOpt, 'getCounterKey').returns(counterKey);
    });
    afterEach(() => {
        setValStub.reset();
        sandbox.restore();
    });
    it('do nothig if state empty', () => {
        getSateStub.returns({});
        const result = getITPProviderHostPrefix(
            win,
            counterOptions,
            senderParams,
        );
        expect(result).to.be.eq('');
        sinon.assert.notCalled(getFNVHashStub);
    });
    it('do nothig without rostelecom provider', () => {
        getSateStub.returns({
            [counterKey]: {
                provider: MEGAFON_KEY,
                status: READY_STATE,
            },
        });
        const result = getITPProviderHostPrefix(
            win,
            counterOptions,
            senderParams,
        );
        expect(result).to.be.eq('');
        sinon.assert.notCalled(getFNVHashStub);
    });
    it('empty prefix with no ready status', () => {
        getSateStub.returns({
            [counterKey]: {
                provider: ROSTELECOM_KEY,
                status: CSP_WAIT,
            },
        });
        const result = getITPProviderHostPrefix(
            win,
            counterOptions,
            senderParams,
        );
        expect(result).to.be.eq('');
        sinon.assert.notCalled(getFNVHashStub);
    });
    it('it set brInfo if it exist', () => {
        getSateStub.returns({
            [counterKey]: {
                provider: ROSTELECOM_KEY,
                status: READY_STATE,
            },
        });
        const result = getITPProviderHostPrefix(
            win,
            counterOptions,
            senderParams,
        );
        expect(result).to.be.eq(`${FNVHashStub}.`);
        sinon.assert.calledOnce(setValStub);
        sinon.assert.calledWith(setValStub, ROSTELECOM_KEY, READY_STATE);
        sinon.assert.calledOnce(getFNVHashStub);
        sinon.assert.calledWith(getFNVHashStub, win, counterOptions);
    });
});
