import * as chai from 'chai';
import * as sinon from 'sinon';
import * as DOM from '@src/utils/dom';
import { fontList } from '@src/utils/browser/font';
import * as fontFactor from '../fonts';

describe('fonts.ts', () => {
    let elemCreateStub: any;
    const sandbox = sinon.createSandbox();
    const testWidth = 100;
    let canvasHTMLElement: any;
    let measureTextStub: sinon.SinonStub<any, any>;
    let contextStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        measureTextStub = sandbox.stub().returns({
            width: testWidth,
        });
        contextStub = sandbox.stub().returns({
            measureText: measureTextStub,
        });
        canvasHTMLElement = {
            getContext: contextStub,
        };
        elemCreateStub = sandbox.stub(DOM, 'getElemCreateFunction');
        elemCreateStub.returns(() => ({ ...canvasHTMLElement } as any));
    });

    afterEach(() => {
        sandbox.restore();
    });
    it('should handle exeption for font setter', () => {
        const fontCtx = { font: 1 };
        sandbox.stub(fontCtx, 'font').set(() => {
            throw new Error("You can't");
        });
        contextStub.returns(fontCtx);
        const result = fontFactor.fontFactor({} as any);
        chai.expect(result).to.be.eq('');
    });
    it('should return empty string if ctx is empty', () => {
        contextStub.returns(null);
        const result = fontFactor.fontFactor({} as any);
        chai.expect(result).to.be.eq('');
    });

    it('should return all base fonts', () => {
        const commonWindowStub = {} as any;
        let counter = 0;
        const maxBits = 5;
        const result = fontFactor.fontFactor(commonWindowStub).split('x');
        chai.expect(result.length).to.be.equal(fontList.length);
        measureTextStub.callsFake(() => {
            let width = testWidth;
            if (counter < maxBits) {
                counter += 1;
            } else {
                width = counter;
            }
            return {
                width,
            };
        });
        const result2 = fontFactor.fontFactor(commonWindowStub).split('x');
        chai.expect(result2.filter((e) => e === 'true').length).to.be.equal(
            maxBits,
        );
    });
});
