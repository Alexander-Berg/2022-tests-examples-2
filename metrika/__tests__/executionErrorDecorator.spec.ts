import Sinon, * as sinon from 'sinon';
import * as chai from 'chai';
import * as log from '@src/utils/logger';
import { ERROR_LOGGER_PROVIDER } from '@src/providers';
import { config } from '@src/config';
import * as random from '@src/utils/number/random';
import * as decorator from '../executionTimeErrorDecorator';
import { TOO_LONG_ERROR_NAME, TOO_LONG_FUNCTION_EXECUTION } from '../consts';
import * as func from '../../function';

const { executionTimeErrorDecorator, getMainThreadBlockingTime } = decorator;
describe('executionTimeErrorDecorator', () => {
    const ctx = {
        location: {
            href: 'http://example.com',
        },
        performance: {
            now: sinon.stub(),
        },
    } as any;
    const callCtx = {} as any;
    const sandbox = sinon.createSandbox();
    let logStub: Sinon.SinonStub;

    const arg1 = 'a';
    const arg2 = 'b';
    const arg3 = 'c';

    beforeEach(() => {
        sandbox.stub(func, 'isNativeFunction').returns(true);
        logStub = sandbox.stub(log, 'log');
        sandbox.stub(random, 'getRandom').returns(1);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('throws errors if callback function does the same', () => {
        ctx.performance.now.returns(0);
        const error = new Error('I am an error');
        const cb = sinon.stub().throws(error);
        const decorated = executionTimeErrorDecorator(cb, 'some', ctx, callCtx);
        chai.expect(() => decorated(arg1, arg2, arg3)).throws(error);
        chai.assert(cb.called);
        chai.expect(cb.getCall(0).args).to.deep.equal([arg1, arg2, arg3]);
        chai.assert(cb.getCall(0).calledOn(callCtx));
        chai.assert(logStub.notCalled);
    });

    it('reports timeout exceedee only on the lowest level', () => {
        const ns1 = 'wrongNs';
        const ns2 = 'correctNs';
        const ns3 = 'anotherWrongNs';

        let timesCalled = 0;
        let accumulatedTime = 0;
        ctx.performance.now.callsFake(() => {
            timesCalled += 1;

            // Грубо говоря коллбэк номер 2 выполнялся больше секунды
            if (timesCalled === 5) {
                accumulatedTime = TOO_LONG_FUNCTION_EXECUTION * 100;
            }

            return accumulatedTime;
        });
        executionTimeErrorDecorator(
            () => {
                executionTimeErrorDecorator(
                    () => {
                        executionTimeErrorDecorator(
                            () => {
                                // do nothing
                            },
                            ns3,
                            ctx,
                            callCtx,
                        )();
                    },
                    ns2,
                    ctx,
                    callCtx,
                )();
            },
            ns1,
            ctx,
            callCtx,
        )();

        sinon.assert.calledOnce(logStub);
        const [errorCtx, logBody, provider] = logStub.getCall(0).args;
        chai.expect(errorCtx).to.equal(ctx);
        chai.expect(logBody).to.deep.equal({
            ['perf']: {
                [config.buildVersion]: {
                    [TOO_LONG_ERROR_NAME]: {
                        [ns2]: ctx.location.href,
                    },
                },
            },
        });
        chai.expect(provider).to.equal(ERROR_LOGGER_PROVIDER);
        chai.expect(getMainThreadBlockingTime()).to.equal(
            TOO_LONG_FUNCTION_EXECUTION * 100,
        );
    });

    it("doesn't report OK timeout", () => {
        let timesCalled = 0;
        ctx.performance.now.callsFake(() => {
            timesCalled += 1;
            return timesCalled * (TOO_LONG_FUNCTION_EXECUTION / 2) - 1;
        });
        const cb = sinon.stub();
        const decorated = executionTimeErrorDecorator(cb, 'some', ctx, callCtx);
        decorated(arg1, arg2, arg3);
        chai.assert(cb.called);
        chai.expect(cb.getCall(0).args).to.deep.equal([arg1, arg2, arg3]);
        chai.assert(cb.getCall(0).calledOn(callCtx));
        chai.assert(logStub.notCalled);
    });
});
