const fs = global.fs = require('fs');
const path = global.path = require('path');

const vm = require('vm');

const base = path.resolve(__dirname, '..', '..');

global.require = require;
global.__dirname = __dirname;
global.__filename = __filename;

function unwrapInclude2 (code, rootDir) {
    return code.replace(/((?:\/\/|\/\*)\s*)?INCLUDE2\s*\(\s*([^\s]+)\s*\)\s*;?/g, (match, comment, file) => {
        if (comment || !file) {
            return '';
        }

        file = file.substr(1, file.length - 2);

        let fullpath = path.join(rootDir, file);

        return unwrapInclude2(fs.readFileSync(fullpath, 'utf-8'));
    });
}

global.INCLUDE = function(includePath) {
    let fullpath = path.join(base, includePath),
        code = fs.readFileSync(fullpath, 'utf-8');

    code = unwrapInclude2(code, base);

    vm.runInThisContext(code, {
        filename: includePath,
        lineOffset: 0,
        columnOffset: 0,
        displayErrors: true
    });
};

global.RAWINC = function(includePath) {
    return global.fs.readFileSync(global.path.join('../', includePath));
};

global.setCounter = function setCounter () {};

var chai = require('chai');
global.should = chai.should();
global.expect = chai.expect;
global.sinon = require('sinon');
chai.use(require('sinon-chai'));
