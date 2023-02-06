const babel = require('@babel/core');
const testPlugin = require('./this-replacing-babel-plugin');
const chai = require("chai");
const chaiJestSnapshot = require("chai-jest-snapshot");

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('this-replacing-babel-plugin', () => {
    before(function() {
        chaiJestSnapshot.resetSnapshotRegistry();
    });

    function testCaseOf(name, code) {
        it(name, () => {
            const {code: res} = babel.transform(code, {
                plugins: [
                    [testPlugin, {}]
                ]
            });
            chai.expect(res).to.matchSnapshot();
        });
    }

    describe('replace of this in global scope', () => {
        testCaseOf('simple', 'this.BEM = function () {};');
        testCaseOf('typeof', 'if (typeof this.Q === undefined) {}');
        testCaseOf('conditional', 'm = 42 ? this.alert : this.confirm');
        testCaseOf('iife 1', '(function (){this.Q =4;})()');
        testCaseOf('iife 2', '~function (){this.Q =4;}()');
        testCaseOf('iife 2', '(function (){this.Q =4;}())');
    });

    describe('no replace of this in global scope', () => {
        testCaseOf('this in function expression', 'var m = function () {this.BEM = 11}');
        testCaseOf('this in function decaration', 'function qq() {this.BEM = 11}');
    });
});
