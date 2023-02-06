'use strict';

const path = require('path');

const {
    PAGES,
    getCommonVariables
} = require('../utils');

const levelsUtil = require('../../../common/levels');

module.exports = function (config) {
    const enbMakeTests = require(config.resolvePath('../common/enb-make-tests.js'));

    enbMakeTests.configMode(config, 'development');
    enbMakeTests.configMode(config, 'builder');
    enbMakeTests.configMode(config, 'teamcity');
    enbMakeTests.configMode(config, 'allure');
    enbMakeTests.configTask(config, PAGES.map(({name}) => `pages/${name}`));

    const specJsTechs = [
        [require('mumu2/techs/enb-webpack-entry')],
        [require('mumu2/techs/enb-webpack'), {
            mode: 'development',
            lang: 'ru',
            configPath: path.resolve(__dirname, '..', '..', '..', 'build', 'getClientWebpackConfig.js'),
            levelsPath: path.resolve(__dirname, '..', '..', '..', 'levels.json'),
            targetBrowsers: ''
        }],
        [require('enb/techs/file-merge'), {
            sources: ['?.ru.bundle.js'],
            target: '?.js'
        }]
    ],
    specCssTechs = function(globalVariables) {
        return [
            [require('enb-stylus/techs/stylus'), {
                target: '?.css',
                sourceSuffixes: ['styl', 'css'],
                autoprefixer: {
                    overrideBrowserslist: ['> 0.5%', 'last 2 versions', 'Firefox ESR', 'OperaMobile >= 12.1', 'Android >= 2', 'iOS >= 6']
                },
                globals: getCommonVariables().concat(globalVariables || []),
                use: [
                    require('mumu2/stylus-use/inline-images')({
                        all: true
                    })
                ],
                imports: false
            }]
        ]
    };

    // Уровни, в которых написаны тесты
    PAGES.forEach((page) => {
        const params = {
            inBrowser: true,
            techs: specJsTechs.concat(specCssTechs(page.variables)),
            gemini: {
                levels: levelsUtil.genGeminiLevels('stream'),
            }
        };

        params.levels = page.levels;

        enbMakeTests.configSpecs(config, ['development', 'teamcity', 'allure', 'builder'], params);
    });
};
