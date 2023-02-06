import {assert} from 'chai';
import attributesGetter from './attributes-getter';

describe('attributes-getter', () => {
    it('should transform _temp', () => {
        const props = {
            _temp: 'aba aba2="caba"'
        };
        const res = attributesGetter(props);
        assert.equal(res, ' aba aba2="caba"');
    });
    it('should transform _temp & temp2', () => {
        const props = {
            _temp: 'aba',
            _temp2: 'aba2="caba1 caba2"'
        };
        const res = attributesGetter(props);
        assert.equal(res, ' aba aba2="caba1 caba2"');
    });
});