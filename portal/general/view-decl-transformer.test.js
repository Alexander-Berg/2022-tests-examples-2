const {transformViewDeclarations} = require('./view-decl-transformer');
const fs = require('fs');
const path = require('path');
const {parse} = require('@babel/parser');
const generate = require('@babel/generator').default;

const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});


describe('transformViewDeclarations', () => {
    it('should transform views call expressions into function declarations', () => {
        const input = fs.readFileSync(path.resolve(__dirname, './fixtures/views-decl-transformer.fixture.js'), { encoding: 'utf-8' });
        const {ast, deps} = transformViewDeclarations(parse(input));
        const output = generate(ast).code;
        chai.expect({output, deps}).to.matchSnapshot();
    });

    it('should transform lambda expressions 1', () => {
        const js = `views('city', (data, req, execView) => execView('checkbox', {name: 'auto'}));`;
        const {ast, deps} = transformViewDeclarations(parse(js));
        const output = generate(ast).code;
        chai.expect({output, deps}).to.matchSnapshot();
    });

    it('should transform lambda expressions 2', () => {
        const js = `views('city', (data, req, execView) => {return execView('checkbox', {name: 'auto'});})`;
        const {ast, deps} = transformViewDeclarations(parse(js));
        const output = generate(ast).code;
        chai.expect({output, deps}).to.matchSnapshot();
    });
});