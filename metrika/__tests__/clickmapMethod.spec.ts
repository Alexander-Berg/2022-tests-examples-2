import * as sinon from 'sinon';
import { useClickmapMethodProvider } from '@src/providers/clickmapMethod';
import * as counterState from '@src/providers/getCounters';
import { COUNTER_STATE_CLICKMAP } from '@src/providers/getCounters/const';

describe('clickMap method', () => {
    const sandbox = sinon.createSandbox();
    const win = {} as Window;
    const counterOptions = { id: 123 };

    let setSpy: sinon.SinonSpy;

    beforeEach(() => {
        setSpy = sandbox.spy();
        sandbox.stub(counterState, 'counterStateSetter').returns(setSpy);
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('set counter state', () => {
        const value = true;
        const method = useClickmapMethodProvider(win, counterOptions as any);
        method(value);
        sinon.assert.calledWith(setSpy, {
            [COUNTER_STATE_CLICKMAP]: value,
        });
    });

    it('default true', () => {
        const method = useClickmapMethodProvider(win, counterOptions as any);
        method();
        sinon.assert.calledWith(setSpy, {
            [COUNTER_STATE_CLICKMAP]: true,
        });
    });
});
