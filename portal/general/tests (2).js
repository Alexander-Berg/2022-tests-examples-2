'use strict';

const path = require('path');
const home = require('../../../configs/current/config');
const {
    getStylusTech,
    BROWSERS
} = require('../techUtils');
const levelsUtil = require('../../../common/levels');
const {getCommonLevels} = require('../utils');

module.exports = function (config) {
    const enbMakeTests = require(config.resolvePath('../common/enb-make-tests.js'));

    config.node('pages-touch/gemini', function (nodeConfig) {
        nodeConfig.addTechs([
            [require('enb-bem-techs/techs/levels'), {
                levels: [
                    'blocks/touch'
                ]
            }],
            [require('enb/techs/file-provider'), {target: '?.bemdecl.js'}],
            require('enb-bem-techs/techs/deps-old'),
            require('enb-bem-techs/techs/files')
        ]);
    });

    enbMakeTests.configMode(config, 'development');
    enbMakeTests.configMode(config, 'builder');
    enbMakeTests.configMode(config, 'teamcity');
    enbMakeTests.configMode(config, 'allure');


    enbMakeTests.configTask(config, [
        'pages-touch/com-mini',
        'pages-touch/index',
        'pages-touch/index-lite',
        'pages-touch/yaru-mini',
        'pages-touch/spok',
        'pages-touch/gramps'
    ]);

    function getJsTechs() {
        return [
            [require('mumu2/techs/enb-webpack-entry')],
            [require('mumu2/techs/enb-webpack'), {
                mode: home.env.devInstance ? 'development' : 'production',
                lang: 'ru',
                configPath: path.resolve(__dirname, '..', '..', '..', 'build', 'getClientWebpackConfig.js'),
                levelsPath: path.resolve(__dirname, '..', '..', '..', 'levels.json'),
                targetBrowsers: BROWSERS
            }],
            [require('enb/techs/file-merge'), {
                sources: ['?.ru.bundle.js'],
                target: '?.js'
            }]
        ];
    }

    function getCSSTechs(mini = false, page) {
        return [
            getStylusTech({
                target: '?.base.css',
                use: [
                    require('mumu2/stylus-use/inline-images')({
                        all: true
                    })
                ]
            }, {
                mini,
                page
            }),
            [require('mumu2/techs/base64-icons'), {
                types: ['combo'],
                sourcesSuffix: 'inline',
                fallbackPrefix: '.no-data-url',
                target: '?.icons.combo.css'
            }],
            [require('mumu2/techs/multifile-merge'), {
                sources: [
                    '?.base.css',
                    '?.icons.combo.css'
                ],
                target: '?.css'
            }]
        ];
    }

    function getSpecParams(mini = false, page) {
        return {
            inBrowser: true,
            techs: getJsTechs().concat(getCSSTechs(mini, page)),
            gemini: {
                levels: levelsUtil.genGeminiLevels('touch')
            }
        };
    }

    [
        'blocks-mini',
        'yaru-mini',
        'com-mini',
        'spok',
        'gramps'
    ].forEach((level) => {
        let params = getSpecParams(true);
        params.levels = [
            '../common/libs/node_modules/@yandex-int/mini-suggest/common.blocks',
            '../common/libs/node_modules/@yandex-int/mini-suggest/touch.blocks',
            '../common/libs/node_modules/@yandex-int/mini-suggest/projects/home/common.blocks',
            '../common/libs/node_modules/@yandex-int/mini-suggest/projects/home/touch.blocks',
            '../common/blocks',
            'blocks/blocks-mini'
        ];

        if (level !== 'blocks-mini') {
            params.levels.push('blocks/' + level);
        }

        enbMakeTests.configSpecs(config, ['development', 'teamcity', 'allure', 'builder'], params);
    });

    (function () {
        [
            {page: 'touch', levels: getCommonLevels()},
        ].forEach(({page, levels}) => {
            let params = getSpecParams(false, page);

            params.levels = [
                {path: '../common/libs/node_modules/@yandex-lego/notifier/common.blocks', check: false},
                '../common/libs/node_modules/@yandex-int/mini-suggest/common.blocks',
                {path: '../common/libs/node_modules/@yandex-lego/notifier/touch-phone.blocks', check: false},
                '../common/libs/node_modules/@yandex-int/mini-suggest/touch.blocks',
                '../common/libs/node_modules/@yandex-int/mini-suggest/projects/home/common.blocks',
                '../common/libs/node_modules/@yandex-int/mini-suggest/projects/home/touch.blocks'
            ].concat(levels);

            enbMakeTests.configSpecs(config, ['development', 'teamcity', 'allure', 'builder'], params);
        });
    })();
};
