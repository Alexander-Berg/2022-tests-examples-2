import * as chai from 'chai';
import { doNotTrack, UNKNOWN_FLAG } from '../doNotTrack';

describe('doNotTrack', () => {
    let commonWindowStub: Window;

    it('doNotTrack enabled', () => {
        commonWindowStub = {
            navigator: {
                doNotTrack: true,
            },
        } as any;
        const result = doNotTrack(commonWindowStub);
        chai.expect(result).to.be.true;
    });

    it('doNotTrack disabled', () => {
        commonWindowStub = {} as any;
        const result = doNotTrack(commonWindowStub);
        chai.expect(result).to.be.equal(UNKNOWN_FLAG);
    });
});
