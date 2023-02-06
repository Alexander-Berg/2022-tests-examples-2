import childMapper from './child-mapper';
import chai from 'chai';

describe('childMapper', () => {
    it('should concat number children', () => {
        const input = [0, 1, 2, 3];
        const output = '0123';
        const result = childMapper(input);
        chai.expect(result).to.be.equal(output);
    });
    it('should concat string children', () => {
        const input = ['string1', 'string2', 'string3', 'string4'];
        const output = 'string1string2string3string4';
        const result = childMapper(input);
        chai.expect(result).to.be.equal(output);
    });
    it('should omit false, null, undefined, and true', () => {
        const input = [false, null, undefined, true];
        const output = '';
        const result = childMapper(input);
        chai.expect(result).to.be.equal(output);
    });
});
