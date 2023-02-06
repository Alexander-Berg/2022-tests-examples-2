import {head__title} from './head.view';
import {expect} from "chai";

describe('head__title', () => {
    it('should return smth', () => {
        const res = head__title(null, {title: 'title'});
        expect(res).to.equal(`title &mdash; Тачевая страница`);
    });
});