import * as chai from 'chai';
import { getAvailScreen } from '../screen';

describe('Screen', () => {
    it('reads availScreen props', () => {
        const result = getAvailScreen({} as any);
        chai.expect(result).to.be.eq('xx');
        const result2 = getAvailScreen({
            screen: {
                availWidth: 1,
                availHeight: 2,
                availTop: 3,
            },
        } as any);
        chai.expect(result2).to.be.eq('1x2x3');
    });
});
