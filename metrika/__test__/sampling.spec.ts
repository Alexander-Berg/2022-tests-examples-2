import * as chai from 'chai';
import * as time from '@src/utils/time';
import * as error from '@src/utils/errorLogger';
import * as lsModule from '@src/storage/localStorage';
import * as sinon from 'sinon';
import * as settingUtils from '@src/utils/counterSettings';
import * as counterInsModule from '@src/utils/counter';
import { CounterOptions } from '@src/utils/counterOptions';
import { METHOD_DESTRUCT } from '@src/providers/destruct/const';
import {
    useWatchSimple,
    WATCH_SAMPLER_DURATION,
    SAMPLING_LS_KEY,
} from '../sampling';

describe('sampling', () => {
    const win = {} as any as Window;
    const sandbox = sinon.createSandbox();
    let timeStub: sinon.SinonStub<any, any>;
    let lsSub: sinon.SinonStub<any, any>;
    let settingStub: sinon.SinonStub<any, any>;
    let errorStub: sinon.SinonStub<any, any>;
    let counsterInstance: sinon.SinonStub<any, any>;
    const counterOptions: CounterOptions = {
        id: Math.random() * 100,
        counterType: '0',
    };
    beforeEach(() => {
        errorStub = sandbox.stub(error, 'ctxErrorLogger');
        errorStub.callsFake((_, fn: Function) => {
            return fn;
        });
        timeStub = sandbox.stub(time, 'TimeOne');
        lsSub = sandbox.stub(lsModule, 'globalLocalStorage');
        settingStub = sandbox.stub(settingUtils, 'getCounterSettings');
        counsterInstance = sandbox.stub(counterInsModule, 'getCounterInstance');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('disable next requests', (done) => {
        const lsMin = 1;
        const currentMin = lsMin + WATCH_SAMPLER_DURATION;
        const getValLsSpy = sandbox.stub().named('getLs').returns(lsMin);
        const setValLsSpy = sandbox.stub().named('setLs').returns(lsMin);
        const desctructSpy = sandbox.stub().named('destruct spy');
        counsterInstance.returns({
            [METHOD_DESTRUCT]: desctructSpy,
        });
        timeStub.returns(() => currentMin);
        lsSub.returns({
            isBroken: false,
            getVal: getValLsSpy,
            setVal: setValLsSpy,
        });
        settingStub.callsFake((_, _1, fn) => {
            fn({
                settings: {
                    // eslint-disable-next-line camelcase
                    c_recp: 0,
                },
            });
            setTimeout(() => {
                sinon.assert.calledWith(
                    setValLsSpy,
                    `${SAMPLING_LS_KEY}${counterOptions.id}:0`,
                    currentMin,
                );
                sinon.assert.calledOnce(desctructSpy);
                done();
            });
            return Promise.resolve();
        });
        const result = useWatchSimple(win, counterOptions);
        sinon.assert.calledOnce(settingStub);
        chai.expect(result).to.be.not.ok;
    });
    it('check counter settings', () => {
        const lsMin = 1;
        const currentMin = lsMin + WATCH_SAMPLER_DURATION;
        const getValLsSpy = sandbox.stub().returns(lsMin);
        timeStub.returns(() => currentMin);
        lsSub.returns({
            isBroken: false,
            getVal: getValLsSpy,
        });
        settingStub.callsFake(() => {
            return Promise.resolve();
        });
        const result = useWatchSimple(win, counterOptions);
        sinon.assert.calledOnce(settingStub);
        chai.expect(result).to.not.ok;
    });
    it('check diff current time and ls value', () => {
        const lsMin = 1;
        const currentMin = lsMin - 1 + WATCH_SAMPLER_DURATION;
        const getValSpy = sandbox.stub().returns(lsMin);
        timeStub.returns(() => currentMin);
        lsSub.returns({
            isBroken: false,
            getVal: getValSpy,
        });
        counsterInstance.returns({});
        const result = useWatchSimple(win, counterOptions);
        sinon.assert.notCalled(settingStub);
        chai.expect(result).to.be.ok;
    });
    it('check local storage avaibility', () => {
        timeStub.returns(() => 1);
        lsSub.returns({
            isBroken: true,
        });
        counsterInstance.returns({});
        const result = useWatchSimple(win, counterOptions);
        sinon.assert.calledWith(counsterInstance, win, counterOptions);
        sinon.assert.calledWith(lsSub, win);
        sinon.assert.calledWith(timeStub, win);
        sinon.assert.notCalled(settingStub);
        chai.expect(result).to.not.ok;
    });
});
