import * as chai from 'chai';
import * as sinon from 'sinon';
import * as funcUtils from '@src/utils/function';
import * as storage from '@src/storage/global';
import { longtaskProvider } from '../longtasks';
import { LONGTASK_KEY } from '../const';

describe('longtask provider', () => {
    const sandbox = sinon.createSandbox();
    const setValGlobalStorage = sandbox.stub();
    let globalStorageStub: sinon.SinonStub;

    beforeEach(() => {
        globalStorageStub = sandbox.stub(storage, 'globalStorage').returns({
            setVal: setValGlobalStorage,
        } as any);
        sandbox
            .stub(funcUtils, 'isNativeFunction')
            .callsFake((name, fn) => !!fn);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('returns noop if PerformanceObserver is not native', () => {
        const unsubscribe = longtaskProvider({} as any);
        chai.expect(unsubscribe).to.equal(funcUtils.noop);
    });

    it('returns noop if observer.observe is broken', () => {
        const observerObserve = sandbox.stub().throws(new Error());
        const observerDisconnect = sinon.stub();
        const win: any = {
            PerformanceObserver: class {
                constructor() {
                    (this as any).observe = observerObserve;
                    (this as any).disconnect = observerDisconnect;
                }
            },
        };
        const unsubscribe = longtaskProvider(win);
        chai.expect(unsubscribe).to.equal(funcUtils.noop);
        const [params] = observerObserve.getCall(0).args;
        chai.expect(params).to.deep.equal({
            type: 'longtask',
            ['buffered']: true,
        });
        sinon.assert.notCalled(observerDisconnect);
    });

    it('collects longtasks info', () => {
        let observerCallback: Function;
        const observerObserve = sandbox.stub();
        const observerDisconnect = sinon.stub();
        const win: any = {
            PerformanceObserver: class {
                constructor(cb: Function) {
                    observerCallback = cb;
                    (this as any).observe = observerObserve;
                    (this as any).disconnect = observerDisconnect;
                }
            },
        };
        const unsubscribe = longtaskProvider(win);
        const [params] = observerObserve.getCall(0).args;
        chai.expect(params).to.deep.equal({
            type: 'longtask',
            ['buffered']: true,
        });
        observerCallback!({
            getEntries: () => [
                { duration: 50 },
                { duration: 150 },
                { duration: 200 },
            ],
        });
        sinon.assert.calledWith(globalStorageStub, win);
        sinon.assert.calledWith(setValGlobalStorage, LONGTASK_KEY, 400);

        unsubscribe();
        sinon.assert.called(observerDisconnect);
    });
});
