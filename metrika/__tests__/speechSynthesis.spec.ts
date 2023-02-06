import * as chai from 'chai';
import { getVoices } from '../speechSynthesis';

describe('speechSynthesis', () => {
    it('getVoices', () => {
        const result = getVoices({} as any);
        chai.expect(result).to.be.eq('');
        const result2 = getVoices({
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
        chai.expect(result2).to.be.deep.eq([1, 2, 3, 4, 5]);
    });
});
