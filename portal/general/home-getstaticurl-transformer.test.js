import {parse} from '@babel/parser';
import {transformGetStaticURL} from './home-getstaticurl-transformer';
import generate from '@babel/generator';

const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

describe('transform home.methodName calls', () => {
    it('should transform home.getStaticURL.getRelative calls', () => {
        const js = `function a(req) {home.getStaticURL.getRelative('/test');}`;
        const ast = transformGetStaticURL(parse(js));
        chai.expect(generate(ast).code).to.matchSnapshot();
    });

    it('should transform home.getStaticURL calls', () => {
        const js = `function a(req) {home.getStaticURL('/test');}`;
        const ast = transformGetStaticURL(parse(js));
        chai.expect(generate(ast).code).to.matchSnapshot();
    });

    it('should throw on unknown property access', () => {
        const js = 'function a(req) {return home.getStaticURL.unknown;}';
        chai.expect(() => transformGetStaticURL(parse(js))).to.throw(/unknown/);
    });

    it ('check req is in scope 1', () => {
        const js = `function a() {home.getStaticURL.getRelative('/test');}`;
        chai.expect(() => transformGetStaticURL(parse(js))).to.throw(/scope/);
    }); 

    it ('check req is in scope 2', () => {
        const js = `function a() {home.getStaticURL('/test');}`;
        chai.expect(() => transformGetStaticURL(parse(js))).to.throw(/scope/);
    }); 
});
