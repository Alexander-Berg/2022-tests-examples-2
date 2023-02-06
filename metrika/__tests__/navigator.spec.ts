import { expect } from 'chai';
import * as sinon from 'sinon';
import * as fn from '@src/utils/function';
import { navigatorFactor } from '../navigator';

describe('navigatorFactor', () => {
    const sandbox = sinon.createSandbox();
    let isNativeStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        isNativeStub = sandbox.stub(fn, 'toNativeOrFalse');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('collects gamepads', () => {
        const result = navigatorFactor({
            navigator: {
                getGamepads: 'hi!',
            },
        } as any);
        expect(result).to.be.eq('xxxxxxxxx0');
    });
    it('collects data from navigator', () => {
        const result = navigatorFactor({} as any);
        expect(result).to.be.eq('xxxxxxxxx0');
        const gamepads = () => ({ length: 10 });
        isNativeStub.withArgs(gamepads, 'getGamepads').returns(gamepads);
        const result2 = navigatorFactor({
            navigator: {
                appName: 1,
                vendor: 2,
                deviceMemory: 3,
                hardwareConcurrency: 4,
                maxTouchPoints: 5,
                appVersion: 6,
                productSub: 7,
                appCodeName: 8,
                vendorSub: 9,
                getGamepads: gamepads,
            },
        } as any);
        expect(result2).to.be.eq('1x2x3x4x5x6x7x8x9x10');
    });
});
