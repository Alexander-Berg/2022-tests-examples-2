var rapidoLang = require('../../run');
var path = require('path');

rapidoLang.run({
    viewMask: 'transforms-views-per-file/blocks/*/*.view.js',
    levels: [{
        "path": "transforms-views-per-file/blocks",
        "view": "home.desktopViews['<folder>']",
        "target": "some.view.js"
    }],
    destDir: 'transforms-views-per-file/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-views-per-file/lang.json',
    command: 'command',
    includePath: 'transforms-views-per-file/blocks',
    output: {
        watch: true
    },
    transforms: [function (fileName, contents, opts) {
        return '// transformed file: (' + path.relative(process.cwd(), fileName) + ')\n' + contents;
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
