/* eslint no-console: 1 */
/* eslint no-eval: 1 */

const fs = global.fs = require('fs');
const path = global.path = require('path');

const base = path.resolve(__dirname, '..', '..');

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

    code = require('module').wrap(code);

    eval(code)(null, require, null, fullpath, path.dirname(fullpath));
};

global.RAWINC = function (includePath) {
    return fs.readFileSync(path.resolve(base, includePath));
};

global.ya = {};
global.error = function() {
    console.log.apply(console, arguments);
};
