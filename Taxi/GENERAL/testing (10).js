const defaultConfig = require('./defaults');
const isFintech = require('../utils/is-fintech');
const {replaceExternalsInBundles} = require('../utils/config-utils');

module.exports = {
    app: {
        version: process.env.BUILD_VER
    },
    bundles: replaceExternalsInBundles(defaultConfig.bundles, [
        {
            regexp: /(http[s]?):\/\/([\w|\d+|.]+)\.([\w|%]+)\/(.+)/,
            replacers: {
                'm.taxi.yandex': {
                    domain: 'm.taxi.taxi.tst.yandex'
                },
                'm.yango.yandex': {
                    domain: 'm.yango.taxi.tst.yandex'
                },
                'tariff.vezet': {
                    domain: 'frontend-vezet.taxi.tst.yandex',
                    tld: 'net'
                }
            }
        }
    ]),
    ...(require(`./${isFintech ? 'fintech' : 'non-fintech'}/testing`))
};
