var techs = {
        // essential
        fileProvider: require('enb/techs/file-provider'),
        fileMerge: require('enb/techs/file-merge'),
        fileCopy: require('enb/techs/file-copy'),

        i18n: require('enb-bem-i18n/techs/i18n'),
        keysets: require('enb-bem-i18n/techs/keysets'),

        // optimization
        borschik: require('enb-borschik/techs/borschik'),

        // css
        postcss: require('enb-postcss/techs/enb-postcss'),
        postcssPlugins: [
            require('postcss-import')(),
            require('postcss-each'),
            require('postcss-for'),
            require('postcss-simple-vars')(),
            require('postcss-calc')(),
            require('postcss-nested'),
            require('rebem-css'),
            require('postcss-url')({ url: 'rebase' }),
            require('autoprefixer')(),
            require('postcss-reporter')()
        ],

        // js
        browserJs: require('enb-js/techs/browser-js'),
        prependYm: require('enb-modules/techs/prepend-modules'),

        // bemtree
        // bemtree: require('enb-bemxjst/techs/bemtree'),

        // bemhtml
        bemhtml: require('enb-bemxjst-i18n/techs/bemhtml-i18n'),
        bemjsonToHtml: require('enb-bemxjst/techs/bemjson-to-html')
    },
    enbBemTechs = require('enb-bem-techs'),
    levels = [
        { path: '../node_modules/bem-core/common.blocks', check: false },
        { path: '../node_modules/bem-core/desktop.blocks', check: false },
        { path: '../node_modules/bem-components/common.blocks', check: false },
        { path: '../node_modules/bem-components/desktop.blocks', check: false },
        { path: '../node_modules/bem-components/design/common.blocks', check: false },
        { path: '../node_modules/bem-components/design/desktop.blocks', check: false },
        { path: '../node_modules/engino/common.blocks', check: false },
        'blocks'
    ];

module.exports = function(config) {
    var isProd = process.env.YENV === 'production';

    config.setLanguages(['en', 'ru']);

    config.nodes('pages/*', function(nodeConfig) {
        nodeConfig.addTechs([
            // essential
            [enbBemTechs.levels, { levels: levels }],
            [techs.fileProvider, { target: '?.bemjson.js' }],
            [enbBemTechs.bemjsonToBemdecl],
            [enbBemTechs.deps],
            [enbBemTechs.files],

            // css
            [techs.postcss, {
                target: '?.css',
                sourceSuffixes: ['post.css', 'styl', 'css'],
                oneOfSourceSuffixes: ['post.css', 'styl', 'css'],
                plugins: techs.postcssPlugins
            }],

            // keyset files for each language
            [techs.keysets, { lang: '{lang}' }],

            // i18n files for each language
            [techs.i18n, { lang: '{lang}' }],

            // bemtree
            // [techs.bemtree, { sourceSuffixes: ['bemtree', 'bemtree.js'] }],

            // bemhtml
            [techs.bemhtml, {
                sourceSuffixes: ['bemhtml', 'bemhtml.js'],
                forceBaseTemplates: true,
                engineOptions : { elemJsInstances : true, escapeContent: true },
                lang: '{lang}',
            }],

            // html
            [techs.bemjsonToHtml, {
                bemhtmlFile: '?.bemhtml.{lang}.js',
                target: '?.{lang}.html'
            }],

            // client bemhtml
            [enbBemTechs.depsByTechToBemdecl, {
                target: '?.bemhtml.bemdecl.js',
                sourceTech: 'js',
                destTech: 'bemhtml'
            }],
            [enbBemTechs.deps, {
                target: '?.bemhtml.deps.js',
                bemdeclFile: '?.bemhtml.bemdecl.js'
            }],
            [enbBemTechs.files, {
                depsFile: '?.bemhtml.deps.js',
                filesTarget: '?.bemhtml.files',
                dirsTarget: '?.bemhtml.dirs'
            }],
            [techs.bemhtml, {
                lang: '{lang}',
                target: '?.browser.{lang}.bemhtml.js',
                filesTarget: '?.bemhtml.files',
                sourceSuffixes: ['bemhtml', 'bemhtml.js'],
                engineOptions : { elemJsInstances : true, escapeContent: true }
            }],

            // js
            [techs.browserJs],
            [techs.fileMerge, {
                target: '?.pre.{lang}.js',
                sources: ['?.lang.{lang}.js', '?.browser.{lang}.bemhtml.js', '?.browser.js'],
                lang: '{lang}'
            }],
            [techs.prependYm, {
                source: '?.pre.{lang}.js',
                target: '?.{lang}.js'
            }],

            // borschik
            [techs.borschik, { source: '?.{lang}.js', target: '?.{lang}.min.js', minify: isProd }],
            [techs.borschik, { source: '?.css', target: '?.min.css', minify: isProd }],

            [techs.fileCopy, { source: '?.ru.html', target: '../../../public/?.html' }],
            [techs.fileCopy, { source: '?.{lang}.html', target: '../../../public/?.{lang}.html' }],
            [techs.fileCopy, { source: '?.min.css', target: '../../../public/?.min.css' }],
            [techs.fileCopy, { source: '?.{lang}.min.js', target: '../../../public/?.{lang}.min.js' }]
        ]);

        nodeConfig.addTargets([/* '?.bemtree.js', */ '?.{lang}.html', '?.min.css', '?.{lang}.min.js',
            '../../../public/?.min.css', '../../../public/?.{lang}.min.js', '../../../public/?.{lang}.html', '../../../public/?.html']);
    });
};
