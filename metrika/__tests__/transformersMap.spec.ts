import * as chai from 'chai';
import * as sinon from 'sinon';
import * as errorModule from '@src/utils/errorLogger';
import { processRawTransformersMap } from '../transformersMap';

describe('processes wrap callbacks into errorLogger', () => {
    const sandbox = sinon.createSandbox();
    let errorLoggerStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        errorLoggerStub = sandbox.stub(errorModule, 'errorLogger');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('processRawTransformersMap', () => {
        errorLoggerStub.callsFake((_, _1, fn) => {
            return fn;
        });
        const doc = {};
        const testCall = () => {
            throw new Error('testError');
        };
        const win = {
            document: doc,
        } as any;
        const item = {
            event: 'testEvent',
            callbacks: [testCall],
        };
        const [result] = processRawTransformersMap(win, [item]);
        chai.expect(result.type).to.be.eq('document');
        chai.expect(result.target).to.be.eq(doc);
        chai.expect(result.callbacks).to.be.lengthOf(1);
        sinon.assert.calledWith(errorLoggerStub, win, `efv.${item.event}`);
        const [newFn] = result.callbacks;
        chai.expect(newFn).to.throws('testError');
    });
});
