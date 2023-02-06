var rapidoLang = require('../../run');
var path = require('path');

rapidoLang.run({
    views: [
        'transforms-simple/blocks/test.view.js'
    ],
    levels: [{
        "path": "transforms-simple/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-simple/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-simple/lang.json',
    command: 'command',
    includePath: 'transforms-simple/blocks',
    output: {
        watch: true
    },
    transforms: [function (fileName, contents, opts) {
        return '// Generated at Tue Feb 16 2016 19:27:17 GMT+0300 (MSK), file: (' + path.relative(process.cwd(), fileName) + ')\n' + contents;
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
