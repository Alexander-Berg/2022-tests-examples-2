import * as sinon from 'sinon';
import * as chai from 'chai';
import { config } from '@src/config';
import { ERROR_LOGGER_PROVIDER, Provider } from '@src/providers';
import * as functionUtils from '@src/utils/function';
import * as flags from '@inject';
import {
    UNIT_TEST_FEATURE,
    DEBUG_FEATURE,
    DEBUG_CONSOLE_FEATURE,
    LOCAL_FEATURE,
    PREPROD_FEATURE,
} from '@generated/features';
import * as logger from '@src/utils/logger';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as execTimeErrDecorator from '../executionTimeErrorDecorator';
import { errorLogger } from '../errorLogger';
import {
    IGNORED_ERRORS,
    KNOWN_ERROR,
    TOO_LONG_FUNCTION_EXECUTION,
} from '../consts';

describe('errorLogger', () => {
    const locationHref = 'https://test.com/';
    const errorMessage = 'nice function!';
    const scope = 'testScope';
    const sandbox = sinon.createSandbox();
    const fn = () => {
        throw new Error(errorMessage);
    };
    let timesCalled = 0;
    let executionTime = 100;
    const { window } = new JSDOMWrapper(undefined, { url: locationHref });
    window.performance.now = () => {
        timesCalled += 1;
        return executionTime * timesCalled;
    };
    const jsErrsKey = 'jserrs';

    let getNativeFunctionStub: sinon.SinonStub<
        [functionName: string, owner: any],
        any
    >;
    let isNativeFunctionStub: sinon.SinonStub<
        [functionName: string, fn: Function],
        boolean
    >;
    let logStub: sinon.SinonStub<
        [ctx: Window, body: any, provider: Provider, counter?: number],
        void
    >;

    beforeEach(() => {
        sandbox.stub(flags, 'flags').value({
            [UNIT_TEST_FEATURE]: false,
            [DEBUG_FEATURE]: false,
            [DEBUG_CONSOLE_FEATURE]: false,
            [LOCAL_FEATURE]: true,
            [PREPROD_FEATURE]: true,
        });
        isNativeFunctionStub = sandbox.stub(functionUtils, 'isNativeFunction');
        isNativeFunctionStub.returns(true);
        getNativeFunctionStub = sandbox.stub(
            functionUtils,
            'getNativeFunction',
        );
        getNativeFunctionStub.returns(123);
        logStub = sandbox.stub(logger, 'log');
        sandbox
            .stub(execTimeErrDecorator, 'executionTimeErrorDecorator')
            .callsFake((f, scopeName, ctx, callContext?) => {
                return f.bind(callContext);
            });
    });

    afterEach(() => {
        timesCalled = 0;
        executionTime = 100;
        sandbox.restore();
    });

    it.skip('reports execution time errors only once in each subtree', () => {
        executionTime = TOO_LONG_FUNCTION_EXECUTION + 1;

        const catchFn = errorLogger(
            window,
            scope,
            () => {
                errorLogger(
                    window,
                    scope,
                    () => {
                        // here
                        errorLogger(window, scope, () => {}, undefined, null)();
                    },
                    undefined,
                    null,
                )();
                errorLogger(
                    window,
                    scope,
                    () => {
                        // here
                        errorLogger(window, scope, () => {}, undefined, null)();
                        // here
                        errorLogger(window, scope, () => {}, undefined, null)();
                    },
                    undefined,
                    null,
                )();
            },
            undefined,
            null,
        );
        catchFn();

        const { args } = logStub.getCall(0);

        sinon.assert.calledThrice(logStub);
        chai.expect(args[0]).to.deep.eq(window);
        chai.expect(args[2]).to.eq(ERROR_LOGGER_PROVIDER);
    });

    it('calls the log fn', () => {
        const catchFn = errorLogger(window, scope, fn, undefined, null);
        catchFn();

        sinon.assert.calledOnce(logStub);
        const { args } = logStub.getCall(0);

        const parsedRequestBody = args[1];

        chai.expect(args[0]).to.eq(window);
        chai.expect(
            parsedRequestBody[jsErrsKey][config.buildVersion][errorMessage][
                scope
            ][locationHref],
        ).to.exist;
        chai.expect(args[2]).to.eq(ERROR_LOGGER_PROVIDER);
    });

    it('ignore specific errors and KNOWN ERROR', () => {
        IGNORED_ERRORS.forEach((error) => {
            const catchFn = errorLogger(
                window,
                scope,
                () => {
                    throw new Error(
                        `a horrible ${error} error occurred by using your code`,
                    );
                },
                undefined,
                null,
            );
            catchFn();
        });

        const catchFn = errorLogger(
            window,
            scope,
            () => {
                throw new Error(KNOWN_ERROR);
            },
            undefined,
            null,
        );
        catchFn();

        chai.expect(logStub.getCalls().length).to.eq(0);
    });
});
