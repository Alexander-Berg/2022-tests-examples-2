require('should');
var fs = require('fs');
var path = require('path');
var freeze = require('../lib/css-freeze-images');

function readFile(name, dir) {
    return fs.readFileSync(path.join(__dirname, dir, name), 'utf-8').trim();
}

function process(name, dir, options) {
    freeze(readFile(name + '.src.css', dir), path.resolve(__dirname, dir), options).should.equal(readFile(name + '.exp.css', dir));
}

describe('css-freeze-images', function () {
    it('не ломается, если нет url(...)', function() {
        process('nourl', 'css-freeze-images');
    });

    it('обрабатывает любые варианты кавычек', function() {
        process('quotes', 'css-freeze-images');
    });

    it('фризит', function() {
        process('freeze', 'css-freeze-images/paths', {freeze: true});
    });
});
