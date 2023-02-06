import * as chai from 'chai';
import Sinon, * as sinon from 'sinon';
import * as errorLogger from '@src/utils/errorLogger';
import { createMethodErrorLogger } from '../methodErrorLogger';

describe('Loggable', () => {
    const sandbox = sinon.createSandbox();
    const errorLoggerResult = 'result';
    let errorLoggerStub: Sinon.SinonStub<any, any>;

    beforeEach(() => {
        errorLoggerStub = sandbox
            .stub(errorLogger, 'errorLogger')
            .returns(errorLoggerResult as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Wraps methods in error logger', () => {
        const ctx: any = {};
        const that: any = {};
        const someMethod = () => {};

        const logger = createMethodErrorLogger(
            ctx,
            that,
            'my_logger',
            'logger_prefix',
        );
        const wrappedMethod = logger.wrapInErrorLogger(someMethod, 'my_method');

        const [loggerCtx, fullNamespace, method, defaultReturn, thatCalled] =
            errorLoggerStub.getCall(0).args;

        chai.expect(wrappedMethod).to.equal(errorLoggerResult);
        chai.expect(loggerCtx).to.equal(ctx);
        chai.expect(fullNamespace).to.equal(
            'logger_prefix.my_logger.my_method',
        );
        chai.expect(method).to.equal(someMethod);
        chai.expect(defaultReturn).to.equal(undefined);
        chai.expect(that).to.equal(thatCalled);
    });
});
