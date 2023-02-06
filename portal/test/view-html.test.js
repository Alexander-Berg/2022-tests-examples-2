require('should');
var fs = require('fs');
var path = require('path');
var viewHtml = require('../view-transforms/view-html');

function readFile (dir, name) {
    return fs.readFileSync(path.join(__dirname, dir, name)).toString().trim();
}

describe('view-html', function () {
    var listEquals = fs.readdirSync(path.join(__dirname, 'view-html-equals'));

    listEquals.forEach(function (name) {
        if (name.indexOf('.view.html') > -1) {
            var base = name.substr(0, name.length - 10);
            it(base, function () {
                var html = readFile('view-html-equals', name);
                var expected = readFile('view-html-equals', base + '.view.js');

                viewHtml(name, html).trim().should.equal(expected);
            });
        }
    });

    it('empty is not allowed', function () {
        try {
            viewHtml('empty.view.html', readFile('view-html', 'empty.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('No template found (empty.view.html)');
        }

        try {
            viewHtml('empty2.view.html', readFile('view-html', 'empty2.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('No template found (empty2.view.html)');
        }

        try {
            viewHtml('empty3.view.html', readFile('view-html', 'empty3.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('No template found (empty3.view.html)');
        }
    });

    it('unexpected comment', function () {
        try {
            viewHtml('unexpected-comment.view.html', readFile('view-html', 'unexpected-comment.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('Unexpected comment, looks similar to template definition (unexpected-comment.view.html)');
        }

        try {
            viewHtml('naming-space.view.html', readFile('view-html', 'naming-space.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('Unexpected comment, looks similar to template definition (naming-space.view.html)');
        }

        try {
            viewHtml('naming-quot.view.html', readFile('view-html', 'naming-quot.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('Unexpected comment, looks similar to template definition (naming-quot.view.html)');
        }

        try {
            viewHtml('naming-hythen.view.html', readFile('view-html', 'naming-hythen.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('Unexpected comment, looks similar to template definition (naming-hythen.view.html)');
        }

        try {
            viewHtml('naming-digit.view.html', readFile('view-html', 'naming-digit.view.html'));
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('Unexpected comment, looks similar to template definition (naming-digit.view.html)');
        }
    });

    it('format option', function () {
        viewHtml('format.view.html', readFile('view-html', 'format.view.html'), {format: false})
            .should.equal(readFile('view-html', 'format.view.js'));
    });

    it('stripComments option', function () {
        viewHtml('comments.view.html', readFile('view-html', 'comments.view.html'), {stripComments: false})
            .trim().should.equal(readFile('view-html', 'comments.view.js'));
    });
});
