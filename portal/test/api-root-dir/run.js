var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'blocks/test.view.js'
    ],
    levels: [{
        "path": "blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'lang.json',
    command: 'command',
    includePath: 'blocks',
    rootDir: 'api-root-dir',
    output: {
        watch: true
    }
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
