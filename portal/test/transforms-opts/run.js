var rapidoLang = require('../../run');
var path = require('path');

rapidoLang.run({
    views: [
        'transforms-opts/blocks/test.view.js'
    ],
    levels: [{
        "path": "transforms-opts/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-opts/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-opts/lang.json',
    command: 'command',
    includePath: 'transforms-opts/blocks',
    output: {
        watch: true
    },
    transforms: [[function (fileName, contents, opts) {
        if (!opts.date) {
            throw 'No opts';
        }
        return '// Generated at ' + opts.date + ', file: (' + path.relative(process.cwd(), fileName) + ')\n' + contents;
    }, {date: 'Tue Feb 16 2016 19:27:17 GMT+0300 (MSK)'}]]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
