import * as chai from 'chai';
import { chromeFactor } from '../chrome';

describe('Antifrod chromeFactor', () => {
    let commonWindowStub: Window;

    it('chromeFactor exist', () => {
        commonWindowStub = {
            chrome: true,
        } as any;
        const result = chromeFactor(commonWindowStub);
        chai.expect(result).to.be.eq(1);
    });

    it('chromeFactor not exist', () => {
        commonWindowStub = {} as any;
        const result = chromeFactor(commonWindowStub);
        chai.expect(result).to.be.eq(0);
    });
});
