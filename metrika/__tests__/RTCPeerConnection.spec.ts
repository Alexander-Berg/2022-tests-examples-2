import * as chai from 'chai';
import { RTCPeerConnectionFactor } from '../RTCPeerConnection';

describe('Antifrod RTCPeerConnectionFactor', () => {
    let commonWindowStub: Window;

    it('RTCPeerConnection exist', () => {
        commonWindowStub = {
            RTCPeerConnection: () => {},
        } as any;
        const result = RTCPeerConnectionFactor(commonWindowStub);
        chai.expect(result).to.be.eq(1);
    });

    it('RTCPeerConnection not exist', () => {
        commonWindowStub = {} as any;
        const result = RTCPeerConnectionFactor(commonWindowStub);
        chai.expect(result).to.be.eq(0);
    });

    it('RTCPeerConnection not a function', () => {
        commonWindowStub = {
            RTCPeerConnection: true,
        } as any;
        const result = RTCPeerConnectionFactor(commonWindowStub);
        chai.expect(result).to.be.eq(0);
    });
});
