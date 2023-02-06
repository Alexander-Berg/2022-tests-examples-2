import {parse} from '@babel/parser';
import {transformHomeMiscCalls} from './home-misc-calls-transformer';
import generate from '@babel/generator';

const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

describe('transform home.methodName calls', () => {
    it('should transform home.methodName calls', () => {
        const js = `
        function a() {
            home.getStaticURL.getRelative('/test');
            home.view('test');
            home.test('test');
            home.test2('test2');
        }`;
        const { ast, homeDeps } = transformHomeMiscCalls(parse(js));
        const result = { homeDeps, code: generate(ast).code };
        chai.expect(result).to.matchSnapshot();
    });

    it ('should throw exception', () => {
        const js = `
            var test = 'asdf';
            function a() {
                home.test('123');
            }
        `;
        chai.expect(() => transformHomeMiscCalls(parse(js))).to.throw(/scope/);
    }); 
});
