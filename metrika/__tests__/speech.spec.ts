import * as chai from 'chai';
import { speechFactor } from '../speech';

describe('speechFactor', () => {
    it('read voices from window', () => {
        const result = speechFactor({} as any);
        chai.expect(result).to.be.eq('');
        const result2 = speechFactor({
            speechSynthesis: {
                test: 1,
                getVoices() {
                    chai.expect(this.test).to.be.eq(1);
                    return [
                        {
                            name: 1,
                            lang: 2,
                            localService: 3,
                            voiceURI: 4,
                            default: 5,
                        },
                    ];
                },
            },
        } as any);
        chai.expect(result2).to.be.eq('1x2x3x4x5');
    });
});
