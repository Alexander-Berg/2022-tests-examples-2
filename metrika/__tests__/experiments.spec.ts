import * as chai from 'chai';
import * as sinon from 'sinon';
import * as providers from '@src/sender';
import { PolyPromise } from '@src/utils';
import { EXPERIMENTS_PROVIDER } from '@src/providers';
import { CounterOptions } from '@src/utils/counterOptions';
import { useExperiments } from '../experiments';

describe('experiments', () => {
    let senderStub: sinon.SinonStub<any, any>;

    const experimentName = 'testGoal';
    const testCtx = {};
    const counterOptions: CounterOptions = {
        id: 10,
        counterType: '0',
    };

    beforeEach(() => {
        senderStub = sinon.stub(providers, 'getSender');
    });
    afterEach(() => {
        senderStub.restore();
    });

    it('return undefined with empty experimentName', () => {
        const winInfo = {} as any;
        senderStub.withArgs(winInfo, EXPERIMENTS_PROVIDER, counterOptions);
        const fn = useExperiments(winInfo, counterOptions);
        const result = fn('');

        chai.expect(result).to.be.an('undefined');
        chai.expect(senderStub.notCalled).to.be.ok;
    });

    it('return undefined without experimentName', () => {
        const winInfo = {} as any;
        senderStub.withArgs(winInfo, EXPERIMENTS_PROVIDER, counterOptions);
        const fn = useExperiments(winInfo, counterOptions);
        const result = fn();

        chai.expect(result).to.be.an('undefined');
        chai.expect(senderStub.notCalled).to.be.ok;
    });

    it('ok without callback and ctx', () => {
        const winInfo = {} as any;
        const promise = PolyPromise.resolve({});
        senderStub
            .withArgs(winInfo, EXPERIMENTS_PROVIDER, counterOptions)
            .returns(() => promise);

        const fn = useExperiments(winInfo, counterOptions);
        fn(experimentName);
        chai.expect(senderStub.called).to.be.ok;
    });

    it('ok with callback without params', () => {
        const callback = sinon.spy();
        const winInfo = {} as any;
        senderStub
            .withArgs(winInfo, EXPERIMENTS_PROVIDER, counterOptions)
            .returns(() => Promise.resolve());

        const fn = useExperiments(winInfo, counterOptions);
        return (fn(experimentName, callback, testCtx) as any).then(() => {
            chai.expect(senderStub.called).to.be.ok;
            chai.expect(callback.called).to.be.ok;
            chai.expect(callback.calledOn(testCtx)).to.be.ok;
        });
    });
});
