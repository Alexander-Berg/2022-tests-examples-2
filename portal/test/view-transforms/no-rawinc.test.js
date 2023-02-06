require('should');
const mockFs = require('mock-fs');
const noRawinc = require('../../view-transforms/no-rawinc');

function testNoRawinc (contents, expected, done, {rootDir = 'root'} = {}) {
    noRawinc('fileName.js', contents, {
        rootDir,
        sync: true
    }).should.deepEqual(expected);

    noRawinc('fileName.js', contents, {
        rootDir,
        sync: false
    }).then(res => {
        res.should.deepEqual(expected);
        done();
    });
}

describe('no-rawinc', () => {
    afterEach(mockFs.restore);

    it('should work', (done) => {
        mockFs({
            'root/some.js': '"use abcde";'
        });
        testNoRawinc('INCLUDE("some.js");', {
            contents: '"use abcde";;',
            deps: ['root/some.js']
        }, done);
    });

    it('should work without special funcs', (done) => {
        mockFs({
            'root/some.js': '"use abcde";'
        });
        testNoRawinc('something();', {
            contents: 'something();',
            deps: []
        }, done);
    });

    it('should work with RAWINC', (done) => {
        mockFs({
            'root/some.js': '"use abcde";'
        });
        testNoRawinc('a = RAWINC("some.js");', {
            contents: 'a = "\\"use abcde\\";";',
            deps: ['root/some.js']
        }, done);
    });

    it('should use specified rootDir', (done) => {
        mockFs({
            'root/some.js': '"use abcde";',
            'root/other/some.js': '"use qwerty";'
        });
        testNoRawinc('a = RAWINC("some.js");', {
            contents: 'a = "\\"use qwerty\\";";',
            deps: ['root/other/some.js']
        }, done, {
            rootDir: 'root/other'
        });
    });

    it('should work with comments', (done) => {
        mockFs({
            'root/some.js': '"use abcde";'
        });
        testNoRawinc('a = "abcde"; // RAWINC("some.js");', {
            contents: 'a = "abcde"; // RAWINC("some.js");',
            deps: []
        }, done);
    });
});
