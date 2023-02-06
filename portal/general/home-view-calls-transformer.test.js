const {transformHomeViewCalls} = require('./home-view-calls-transformer');
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

describe('transformHomeViewCalls', () => {
    it('should transform home.view call expressions', () => {
        const input = fs.readFileSync(path.resolve(__dirname, './fixtures/home-view-calls-transformer.fixture.js'), { encoding: 'utf-8' });
        const {ast, deps} = transformHomeViewCalls(parse(input));
        const output = generate(ast).code;
        chai.expect({output, deps}).to.matchSnapshot();
    });
});