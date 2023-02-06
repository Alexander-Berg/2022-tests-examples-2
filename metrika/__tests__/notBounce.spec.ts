import * as chai from 'chai';
import * as sinon from 'sinon';
import * as userTimeDefer from '@src/utils/userTimeDefer';
import * as sender from '@src/sender';
import * as flags from '@inject';
import * as getCountersUtils from '@src/providers/getCounters';
import * as errorLoggerUtils from '@src/utils/errorLogger';
import { CounterOptions } from '@src/utils/counterOptions';
import { SenderInfo } from '@src/sender/SenderInfo';
import { ARTIFICIAL_BR_KEY } from '@src/providers/artificialHit/type';
import { getRandom } from '@src/utils/number';
import * as counterSettingsStore from '@src/utils/counterSettings';
import * as time from '@src/utils/time';
import { COUNTER_STATE_NOT_BOUNCE } from '@src/providers/getCounters/const';
import {
    PREPROD_FEATURE,
    RESOURCES_TIMINGS_FEATURE,
} from '@generated/features';
import { useNotBounceProviderRaw } from '../notBounce';
import {
    NOT_BOUNCE_BR_KEY,
    NOT_BOUNCE_CLIENT_TIME_BR_KEY,
    DEFAULT_NOT_BOUNCE_TIMEOUT,
} from '../const';

describe('notBounce.ts', () => {
    const window = { Math } as Window;
    let senderInfo: SenderInfo | undefined;
    const timeouts: [number, Function][] = [];
    const sandbox = sinon.createSandbox();

    let counterStateStub: sinon.SinonStub;
    let setUserTimeDeferStub: sinon.SinonStub;
    let clearUserTimeDeferStub: sinon.SinonStub;
    let getSenderStub: sinon.SinonStub;
    let senderSpy: sinon.SinonSpy;
    let stateGetterStub: sinon.SinonStub;

    const getCounterOpt = (val: any): CounterOptions => ({
        id: getRandom(window, 100),
        counterType: '0',
        accurateTrackBounce: val,
    });
    const verifyCounterStateCall = (callIndex: number, expectedValue: any) => {
        const { args } = counterStateStub.getCall(callIndex);
        chai.expect(args[0]).to.deep.eq({ accurateTrackBounce: expectedValue });
        chai.expect(args.length).to.eq(1);
    };

    let randomStub: any;

    beforeEach(() => {
        sandbox
            .stub(counterSettingsStore, 'getCounterSettings')
            .callsFake((ctx, opts, cb) => {
                cb({ firstHitClientTime: 100 } as any);

                return Promise.resolve();
            });

        sandbox.stub(flags, 'flags').value({
            [RESOURCES_TIMINGS_FEATURE]: true,
            [PREPROD_FEATURE]: false,
        });
        sandbox.stub(time, 'TimeOne').returns((() => 0) as any);
        senderInfo = undefined;
        timeouts.splice(0, timeouts.length);

        randomStub = sandbox.stub(Math, 'random');
        randomStub.returns(0.01);

        setUserTimeDeferStub = sandbox.stub(userTimeDefer, 'setUserTimeDefer');
        setUserTimeDeferStub.callsFake(
            (ctx: Window, callback: Function, t: number) => {
                return {
                    id: timeouts.push([t, callback]) + 1,
                };
            },
        );

        clearUserTimeDeferStub = sandbox.stub(
            userTimeDefer,
            'clearUserTimeDefer',
        );
        clearUserTimeDeferStub.callsFake((timeoutId: number) => {
            timeouts.splice(timeoutId - 1, 1);
        });

        senderSpy = sinon.spy((senderOpt: SenderInfo) => {
            senderInfo = senderOpt;

            return Promise.resolve('done');
        });
        getSenderStub = sandbox.stub(sender, 'getSender');
        getSenderStub.returns(senderSpy);

        sandbox
            .stub(errorLoggerUtils, 'errorLogger')
            .callsFake((...args: unknown[]) => args[args.length - 1] as any);
        counterStateStub = sandbox.stub();
        sandbox
            .stub(getCountersUtils, 'counterStateSetter')
            .returns(counterStateStub);
        stateGetterStub = sandbox
            .stub(getCountersUtils, 'counterStateGetter')
            .returns(() => ({ [COUNTER_STATE_NOT_BOUNCE]: undefined }));
    });

    afterEach(() => {
        sandbox.restore();
        senderSpy.resetHistory();
    });

    it('Does nothing if no accurateTrackBounce is set', () => {
        const { notBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(undefined),
        );
        chai.expect(timeouts.length).to.equal(0);
        chai.expect(typeof notBounce).to.equal('function');
    });

    it('Sets timeout if accurateTrackBounce is set and clears timeout if returned callback called', () => {
        const { notBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(200),
        );
        chai.expect(timeouts).to.have.lengthOf(1);
        notBounce();
        const { brInfo } = senderInfo!;
        chai.expect(brInfo!.getVal(NOT_BOUNCE_BR_KEY)).to.equal('1');
        chai.expect(brInfo!.getVal(NOT_BOUNCE_CLIENT_TIME_BR_KEY)).to.equal(
            100,
        );
        chai.expect(brInfo!.getVal(ARTIFICIAL_BR_KEY)).to.equal('1');
        chai.expect(timeouts).to.have.lengthOf(0);
    });

    it('Sets default timeout if accurateTrackBounce is set to true', () => {
        useNotBounceProviderRaw(window, getCounterOpt(true));
        const [timeout, callback] = timeouts[0];
        chai.expect(timeout).to.equal(DEFAULT_NOT_BOUNCE_TIMEOUT);
        chai.expect(typeof callback).to.equal('function');
    });

    it('Sets counter state', () => {
        const { notBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(true),
        );

        verifyCounterStateCall(0, true);
        notBounce();
        verifyCounterStateCall(1, true);
    });

    it('Make request on repeat call', () => {
        const { notBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(false),
        );
        notBounce();
        chai.expect(senderSpy.called).to.be.ok;
    });

    it('Use accurateTrackBounce method', () => {
        const testTimeout = 123;
        const { accurateTrackBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(undefined),
        );
        chai.expect(timeouts.length).to.equal(0);
        accurateTrackBounce(testTimeout);
        const [timeout, callback] = timeouts[0];
        chai.expect(timeouts.length).to.equal(1);
        chai.expect(timeout).to.equal(testTimeout);
        chai.expect(typeof callback).to.equal('function');
    });

    it('Call accurateTrackBounce once', () => {
        stateGetterStub.returns(() => ({ [COUNTER_STATE_NOT_BOUNCE]: true }));
        const { accurateTrackBounce } = useNotBounceProviderRaw(
            window,
            getCounterOpt(undefined),
        );
        accurateTrackBounce();
        chai.expect(timeouts.length).to.equal(0);
    });
});
