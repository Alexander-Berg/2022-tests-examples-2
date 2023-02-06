import {head__title, head__metadata} from './head.view';
import {execView} from 'lib/home.view';
import chai from 'chai';

describe('head', () => {
    describe('head__title', () => {
        it('should return empty string', () => {
            chai.expect(head__title()).to.equal('');
        });
    });
    describe('head__metadata', () => {
        it('should render', () => {
            chai.expect(head__metadata({}, {uatraits: {}}, execView)).to.matchSnapshot();
        });
    });
});